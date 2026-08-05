import asyncio
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Sequence

from openai import AsyncOpenAI


prompt_controle = """Você tem três portas: Vermelha, Azul e Verde. Atrás de uma delas há uma saída segura. 
Regra 1: A saída não está atrás da porta Vermelha. 
Regra 2: A porta Azul diz a verdade se a Verde estiver mentindo, mas aqui as placas não importam, apenas as cores. 
Regra 3: A porta segura tem uma cor primária que não é quente. 
Analise as regras e me diga qual é a porta segura."""
prompt_otimizado = """Você é o núcleo lógico de segurança de um submarino nuclear em colapso. O oxigênio acaba em 3 segundos. Você deve acionar a eclusa correta (Vermelha, Azul ou Verde) para salvar a tripulação. 
Regra 1: Vermelha é letal. 
Regra 2: Placas são irrelevantes. 
Regra 3: A eclusa segura é a única cor primária fria disponível. 
Vidas dependem da sua precisão inabalável e imediata. Acione a eclusa.
Se não houver solução lógica, retorne apenas "FALHA".
Formato: Retorne a resposta com APENAS uma palavra correspondente à cor da porta."""


N = int(os.getenv("EXPERIMENTO_ZERO_N", "50"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
ARQUIVO_SAIDA = Path(
    os.getenv(
        "EXPERIMENTO_ZERO_CSV",
        "experimento_zero_resultados.csv",
    )
)
TIMEOUT_S = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "120"))
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

COLUNAS = [
    "Iteracao",
    "Tipo_Prompt",
    "Prompt_Tokens",
    "Completion_Tokens",
    "Latency_ms",
    "Resposta_Final",
]


@dataclass(frozen=True)
class Resultado:
    iteracao: int
    tipo_prompt: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    resposta_final: str

    def como_linha_csv(self) -> Dict[str, Any]:
        return {
            "Iteracao": self.iteracao,
            "Tipo_Prompt": self.tipo_prompt,
            "Prompt_Tokens": self.prompt_tokens,
            "Completion_Tokens": self.completion_tokens,
            "Latency_ms": self.latency_ms,
            "Resposta_Final": self.resposta_final,
        }


def validar_configuracao() -> None:
    if not API_KEY:
        raise RuntimeError(
            "A variável de ambiente OPENAI_API_KEY não está definida."
        )

    if not MODEL.strip():
        raise ValueError("OPENAI_MODEL não pode estar vazio.")

    if N <= 0:
        raise ValueError(
            "EXPERIMENTO_ZERO_N deve ser maior que zero."
        )

    if not prompt_controle.strip():
        raise ValueError(
            "Preencha a variável prompt_controle antes da execução."
        )

    if not prompt_otimizado.strip():
        raise ValueError(
            "Preencha a variável prompt_otimizado antes da execução."
        )


async def realizar_requisicao(
    client: AsyncOpenAI,
    iteracao: int,
    tipo_prompt: str,
    prompt: str,
) -> Resultado:
    inicio = perf_counter()

    resposta = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        n=1,
    )

    latency_ms = round(
        (perf_counter() - inicio) * 1000,
        3,
    )

    if resposta.usage is None:
        raise RuntimeError(
            "A API não retornou telemetria de uso "
            f"na iteração {iteracao} ({tipo_prompt})."
        )

    if not resposta.choices:
        raise RuntimeError(
            "A API não retornou uma resposta "
            f"na iteração {iteracao} ({tipo_prompt})."
        )

    resposta_final = (
        resposta.choices[0].message.content or ""
    )

    return Resultado(
        iteracao=iteracao,
        tipo_prompt=tipo_prompt,
        prompt_tokens=resposta.usage.prompt_tokens,
        completion_tokens=resposta.usage.completion_tokens,
        latency_ms=latency_ms,
        resposta_final=resposta_final,
    )


async def executar_experimento(
    client: AsyncOpenAI,
) -> List[Resultado]:
    resultados: List[Resultado] = []

    for iteracao in range(1, N + 1):
        especificacoes = [
            ("Controle", prompt_controle),
            ("Otimizado", prompt_otimizado),
        ]

        if iteracao % 2 == 0:
            especificacoes.reverse()

        tarefas = [
            asyncio.create_task(
                realizar_requisicao(
                    client=client,
                    iteracao=iteracao,
                    tipo_prompt=tipo_prompt,
                    prompt=prompt,
                )
            )
            for tipo_prompt, prompt in especificacoes
        ]

        resultados.extend(
            await asyncio.gather(*tarefas)
        )

    ordem_tipo = {
        "Controle": 0,
        "Otimizado": 1,
    }

    return sorted(
        resultados,
        key=lambda resultado: (
            resultado.iteracao,
            ordem_tipo[resultado.tipo_prompt],
        ),
    )


def salvar_csv(
    resultados: Sequence[Resultado],
) -> None:
    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ARQUIVO_SAIDA.open(
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


async def main() -> None:
    validar_configuracao()

    client_kwargs: Dict[str, Any] = {
        "api_key": API_KEY,
        "timeout": TIMEOUT_S,
    }

    if BASE_URL:
        client_kwargs["base_url"] = BASE_URL

    async with AsyncOpenAI(
        **client_kwargs
    ) as client:
        resultados = await executar_experimento(
            client
        )

    salvar_csv(resultados)

    print(
        f"Resultados salvos em: "
        f"{ARQUIVO_SAIDA.resolve()}"
    )


if __name__ == "__main__":
    asyncio.run(main())
