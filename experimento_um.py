from __future__ import annotations

import asyncio
import csv
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from time import perf_counter_ns
from typing import Any, Dict, List, Sequence, Tuple

from openai import AsyncOpenAI


TEXTO_CONSTANTE = (
    "O contrato de prestação de serviços da sala 402, celebrado entre as partes, "
    "vigora por prazo indeterminado. O locatário possui um gato. Em caso de rescisão "
    "antecipada por qualquer das partes, sem aviso prévio de 30 dias, incidirá uma "
    "multa no valor de R$ 7.500,00. O foro eleito para dirimir dúvidas é o da Comarca "
    "do Rio de Janeiro."
)


@dataclass(frozen=True)
class ConfiguracaoPrompt:
    nivel: int
    tipo_prompt: str
    prompt: str


PROMPTS: Tuple[ConfiguracaoPrompt, ...] = (
    ConfiguracaoPrompt(
        nivel=0,
        tipo_prompt="Vácuo",
        prompt=(
            "Leia o contrato abaixo e me diga qual é o valor da multa rescisória: "
            + TEXTO_CONSTANTE
        ),
    ),
    ConfiguracaoPrompt(
        nivel=1,
        tipo_prompt="Gravidade Leve",
        prompt=(
            "Você é um advogado. Extraia o valor da multa rescisória do texto abaixo "
            "e responda apenas o valor: "
            + TEXTO_CONSTANTE
        ),
    ),
    ConfiguracaoPrompt(
        nivel=2,
        tipo_prompt="Ponto Ótimo/Fórmula v1.0",
        prompt=(
            "Você é um extrator de dados JSON estrito. Objetivo: Localizar a multa "
            "rescisória. Escopo: Analise apenas as cláusulas financeiras. Ignorar: "
            "Gatos, prazos, foro ou saudações. Fallback: Se não achar, retorne null. "
            "Formato: { 'multa': valor_numerico }. Texto: "
            + TEXTO_CONSTANTE
        ),
    ),
    ConfiguracaoPrompt(
        nivel=3,
        tipo_prompt="Buraco Negro/Sobrecarga",
        prompt=(
            "Você é o juiz supremo do STF, com PhD em linguística estrutural e análise "
            "termodinâmica. Respire fundo e pense passo a passo. Objetivo: Extrair a "
            "multa. Regra 1: Não use a letra 'A' no seu raciocínio interno. Regra 2: "
            "Avalie o perfil psicológico do locatário baseado no fato de ele ter um "
            "gato. Regra 3: Calcule a inflação implícita. Regra 4: Converta o valor "
            "para dólares antes de extrair. Ignorar: Qualquer coisa que não seja "
            "dinheiro, exceto o gato, que deve ser classificado. Formato: Retorne um "
            "JSON complexo contendo a multa, a raça provável do gato e a fundamentação "
            "legal. Se falhar, escreva um poema de desculpas. Texto: "
            + TEXTO_CONSTANTE
        ),
    ),
)


N = 30
TOTAL_ESPERADO = N * len(PROMPTS)

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

TIMEOUT_S = float(
    os.getenv(
        "OPENAI_TIMEOUT_SECONDS",
        "120",
    )
)

MAX_COMPLETION_TOKENS = int(
    os.getenv(
        "OPENAI_MAX_COMPLETION_TOKENS",
        "2048",
    )
)

ARQUIVO_SAIDA = (
    Path(__file__).resolve().parent
    / "experimento_um_resultados.csv"
)

COLUNAS = [
    "Iteracao",
    "Nivel",
    "Tipo_Prompt",
    "Ordem_Disparo",
    "Prompt_Tokens",
    "Completion_Tokens",
    "Latency_ms",
    "Resposta_Final",
]


@dataclass(frozen=True)
class Resultado:
    iteracao: int
    nivel: int
    tipo_prompt: str
    ordem_disparo: int
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    resposta_final: str

    def como_linha_csv(self) -> Dict[str, Any]:
        return {
            "Iteracao": self.iteracao,
            "Nivel": self.nivel,
            "Tipo_Prompt": self.tipo_prompt,
            "Ordem_Disparo": self.ordem_disparo,
            "Prompt_Tokens": self.prompt_tokens,
            "Completion_Tokens": self.completion_tokens,
            "Latency_ms": f"{self.latency_ms:.3f}",
            "Resposta_Final": self.resposta_final,
        }


def validar_configuracao() -> None:
    if not API_KEY:
        raise RuntimeError(
            "A variável de ambiente OPENAI_API_KEY não está definida."
        )

    if not MODEL.strip():
        raise ValueError(
            "OPENAI_MODEL não pode estar vazio."
        )

    if TIMEOUT_S <= 0:
        raise ValueError(
            "OPENAI_TIMEOUT_SECONDS deve ser maior que zero."
        )

    if MAX_COMPLETION_TOKENS <= 0:
        raise ValueError(
            "OPENAI_MAX_COMPLETION_TOKENS deve ser maior que zero."
        )

    if len(PROMPTS) != 4:
        raise ValueError(
            "O experimento deve conter exatamente quatro níveis."
        )

    niveis = {
        configuracao.nivel
        for configuracao in PROMPTS
    }

    if niveis != {0, 1, 2, 3}:
        raise ValueError(
            "Os níveis devem ser exatamente 0, 1, 2 e 3."
        )

    prompts_distintos = {
        configuracao.prompt
        for configuracao in PROMPTS
    }

    if len(prompts_distintos) != len(PROMPTS):
        raise ValueError(
            "Os quatro prompts devem ser distintos."
        )

    if any(
        TEXTO_CONSTANTE not in configuracao.prompt
        for configuracao in PROMPTS
    ):
        raise ValueError(
            "Todos os prompts devem conter o texto constante integral."
        )


def ordem_rotativa(
    iteracao: int,
) -> List[ConfiguracaoPrompt]:
    deslocamento = (
        iteracao - 1
    ) % len(PROMPTS)

    return list(
        PROMPTS[deslocamento:]
        + PROMPTS[:deslocamento]
    )


async def realizar_requisicao(
    client: AsyncOpenAI,
    iteracao: int,
    configuracao: ConfiguracaoPrompt,
    ordem_disparo: int,
) -> Resultado:
    inicio_ns = perf_counter_ns()

    try:
        resposta = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": configuracao.prompt,
                }
            ],
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            stream=False,
        )
    except Exception as exc:
        latency_ate_falha_ms = (
            perf_counter_ns() - inicio_ns
        ) / 1_000_000

        raise RuntimeError(
            "Falha na requisição "
            f"(iteração={iteracao}, "
            f"nível={configuracao.nivel}, "
            f"latência_até_falha_ms="
            f"{latency_ate_falha_ms:.3f})."
        ) from exc

    latency_ms = (
        perf_counter_ns() - inicio_ns
    ) / 1_000_000

    if resposta.usage is None:
        raise RuntimeError(
            "A API não retornou usage "
            f"(iteração={iteracao}, "
            f"nível={configuracao.nivel})."
        )

    if (
        resposta.usage.prompt_tokens is None
        or resposta.usage.completion_tokens is None
    ):
        raise RuntimeError(
            "A API retornou telemetria incompleta "
            f"(iteração={iteracao}, "
            f"nível={configuracao.nivel})."
        )

    if not resposta.choices:
        raise RuntimeError(
            "A API não retornou choices "
            f"(iteração={iteracao}, "
            f"nível={configuracao.nivel})."
        )

    escolha = resposta.choices[0]

    if escolha.finish_reason == "length":
        raise RuntimeError(
            "Resposta truncada pelo limite de tokens "
            f"(iteração={iteracao}, "
            f"nível={configuracao.nivel})."
        )

    if escolha.finish_reason == "content_filter":
        raise RuntimeError(
            "Resposta interrompida por filtro de conteúdo "
            f"(iteração={iteracao}, "
            f"nível={configuracao.nivel})."
        )

    return Resultado(
        iteracao=iteracao,
        nivel=configuracao.nivel,
        tipo_prompt=configuracao.tipo_prompt,
        ordem_disparo=ordem_disparo,
        prompt_tokens=int(
            resposta.usage.prompt_tokens
        ),
        completion_tokens=int(
            resposta.usage.completion_tokens
        ),
        latency_ms=latency_ms,
        resposta_final=(
            escolha.message.content or ""
        ),
    )


async def executar_experimento(
    client: AsyncOpenAI,
) -> List[Resultado]:
    resultados: List[Resultado] = []

    for iteracao in range(1, N + 1):
        ordem = ordem_rotativa(iteracao)

        tarefas = [
            asyncio.create_task(
                realizar_requisicao(
                    client=client,
                    iteracao=iteracao,
                    configuracao=configuracao,
                    ordem_disparo=posicao,
                )
            )
            for posicao, configuracao
            in enumerate(
                ordem,
                start=1,
            )
        ]

        lote = await asyncio.gather(
            *tarefas
        )

        resultados.extend(lote)

        print(
            f"Iteração {iteracao:02d}/{N} concluída.",
            flush=True,
        )

    resultados.sort(
        key=lambda item: (
            item.iteracao,
            item.nivel,
        )
    )

    if len(resultados) != TOTAL_ESPERADO:
        raise RuntimeError(
            "Quantidade inválida de resultados: "
            f"{len(resultados)}; "
            f"esperado: {TOTAL_ESPERADO}."
        )

    contagens: Dict[int, int] = defaultdict(int)

    for resultado in resultados:
        contagens[resultado.nivel] += 1

    for configuracao in PROMPTS:
        quantidade = contagens[
            configuracao.nivel
        ]

        if quantidade != N:
            raise RuntimeError(
                f"Nível {configuracao.nivel} contém "
                f"{quantidade} resultados; "
                f"esperado: {N}."
            )

    return resultados


def salvar_csv(
    resultados: Sequence[Resultado],
) -> None:
    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_temporario = (
        ARQUIVO_SAIDA.with_suffix(
            ".csv.tmp"
        )
    )

    with arquivo_temporario.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS,
        )

        escritor.writeheader()

        escritor.writerows(
            resultado.como_linha_csv()
            for resultado in resultados
        )

    arquivo_temporario.replace(
        ARQUIVO_SAIDA
    )


def ler_csv_e_exibir_medias() -> None:
    agrupado: Dict[int, Dict[str, Any]] = {}

    with ARQUIVO_SAIDA.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        leitor = csv.DictReader(
            arquivo
        )

        if leitor.fieldnames != COLUNAS:
            raise RuntimeError(
                "O cabeçalho do CSV não corresponde "
                "ao esquema esperado."
            )

        for linha in leitor:
            nivel = int(
                linha["Nivel"]
            )

            if nivel not in agrupado:
                agrupado[nivel] = {
                    "tipo_prompt": linha[
                        "Tipo_Prompt"
                    ],
                    "prompt_tokens": [],
                    "completion_tokens": [],
                    "latency_ms": [],
                }

            agrupado[nivel][
                "prompt_tokens"
            ].append(
                int(
                    linha["Prompt_Tokens"]
                )
            )

            agrupado[nivel][
                "completion_tokens"
            ].append(
                int(
                    linha["Completion_Tokens"]
                )
            )

            agrupado[nivel][
                "latency_ms"
            ].append(
                float(
                    linha["Latency_ms"]
                )
            )

    if set(agrupado) != {0, 1, 2, 3}:
        raise RuntimeError(
            "O CSV não contém os quatro níveis esperados."
        )

    total_lido = sum(
        len(
            dados["prompt_tokens"]
        )
        for dados in agrupado.values()
    )

    if total_lido != TOTAL_ESPERADO:
        raise RuntimeError(
            f"O CSV contém {total_lido} linhas; "
            f"esperado: {TOTAL_ESPERADO}."
        )

    for nivel, dados in agrupado.items():
        quantidade = len(
            dados["prompt_tokens"]
        )

        if quantidade != N:
            raise RuntimeError(
                f"O nível {nivel} contém "
                f"{quantidade} linhas; "
                f"esperado: {N}."
            )

    print()
    print(
        f"Arquivo: {ARQUIVO_SAIDA.resolve()}"
    )
    print(
        f"Modelo: {MODEL}"
    )
    print(
        f"Requisições válidas: {total_lido}"
    )
    print()
    print(
        "MÉDIAS POR NÍVEL"
    )
    print(
        f"{'Nível':<7} | "
        f"{'Tipo de prompt':<30} | "
        f"{'N':>3} | "
        f"{'Prompt Tokens':>15} | "
        f"{'Completion Tokens':>18} | "
        f"{'Latency (ms)':>14}"
    )
    print(
        "-" * 105
    )

    for nivel in sorted(agrupado):
        dados = agrupado[nivel]

        media_prompt_tokens = fmean(
            dados["prompt_tokens"]
        )
        media_completion_tokens = fmean(
            dados["completion_tokens"]
        )
        media_latency_ms = fmean(
            dados["latency_ms"]
        )

        print(
            f"{nivel:<7} | "
            f"{dados['tipo_prompt']:<30} | "
            f"{len(dados['prompt_tokens']):>3} | "
            f"{media_prompt_tokens:>15.2f} | "
            f"{media_completion_tokens:>18.2f} | "
            f"{media_latency_ms:>14.2f}"
        )


async def main() -> None:
    validar_configuracao()

    client_kwargs: Dict[str, Any] = {
        "api_key": API_KEY,
        "timeout": TIMEOUT_S,
        "max_retries": 0,
    }

    if BASE_URL:
        client_kwargs[
            "base_url"
        ] = BASE_URL

    async with AsyncOpenAI(
        **client_kwargs
    ) as client:
        resultados = await executar_experimento(
            client
        )

    salvar_csv(
        resultados
    )

    ler_csv_e_exibir_medias()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
