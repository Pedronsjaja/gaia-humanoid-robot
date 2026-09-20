# CBR — futebol de robôs humanoides

[Início](../../README.md) · [Estrutura](../estrutura/README.md) · [Eletrônica](../eletronica/README.md) · [Programação](../programacao/README.md)

**Objetivo indicado pela equipe: CBR, categoria Humanoid.** A subcategoria (Regular ou Entry-Level), o ano de inscrição e o porte final ainda precisam ser confirmados. Este guia orienta o projeto; não declara o Gaia aprovado para competir.

## Qual regulamento estamos usando?

Consulta em **20/09/2026**:

| Documento | Situação | Como usar |
| --- | --- | --- |
| [Página CBR de categorias](https://cbr.robocup.org.br/index.php/categorias/) | Publica Humanoid Regular e Entry-Level | Confirmar categoria com organização |
| Link “Regras 2026” dessa página | Aponta para `2026/08/RC-HL-2025-Rules.pdf`; retornou HTTP 404 | **Edição aplicável pendente de confirmação** |
| [CBR Humanoid 2025 — cópia](regulamentos/cbr-humanoid-2025.pdf) | Documento histórico, versão 0.0.6 | Referência provisória e levantamento de dúvidas |
| [Humanoid League 2025 — cópia](regulamentos/humanoid-league-2025.pdf) | Regulamento internacional histórico | Comparar; não substitui a regra local CBR |
| [CBR Entry-Level 2024](https://cbr.robocup.org.br/wp-content/uploads/2024/06/CBR-2024-Regras-e-Desafios-Humanoide-EL.pdf) | Histórico específico de outra subcategoria | Não aplicar automaticamente à Regular/2026 |
| [HSL internacional](https://hsl.robocup.org/) | Liga internacional reorganizada em 2026 | Contexto, não escolha normativa do Gaia |

Não use uma página descritiva de categorias como única especificação dimensional. O regulamento detalhado e os esclarecimentos oficiais da edição escolhida devem prevalecer.

## Limitações que afetam o projeto

**Referência histórica: CBR2025-Humanoid, §§4.2–4.5; páginas do PDF 13–18. Não são requisitos confirmados para 2026.**

| Área | Regra histórica resumida |
| --- | --- |
| Corpo | Tronco, cabeça, dois braços e duas pernas; alça; locomoção bípede e recuperação de queda |
| Altura KidSize, §4.3 | 40–90 cm; a introdução diverge e menciona 40–100 cm |
| Pés | Área envolvente ≤ (2,2 × HCOM)²/32; razão de lados ≤ 2,5 |
| Proporções | Cilindro: diâmetro 0,55 × Htop; pernas 0,35–0,7 × Htop; cabeça 0,05–0,25 × Htop |
| Visão | Até duas câmeras sobrepostas na cabeça; campo visual limitado; pan ±135°, tilt ±90° |
| Sensores | Restrições a sensores externos ativos; magnetômetro terrestre não pode orientar o software |
| Rede | Rede oficial; banda de 1 Mbit/s por equipe; restrição de comandos externos |
| Arbitragem | Estados/penalidades via GameController UDP |

Fonte: [PDF oficial CBR 2025](https://cbr.robocup.org.br/wp-content/uploads/2025/07/CBR2025-Humanoid.pdf), §§4.2–4.5. Htop é altura em pé; HCOM é altura do centro de massa. Consulte definições e outras proporções no documento completo.

O texto também contém inconsistência entre referências a WLAN/Ethernet no §4.5. **Altura aplicável e rede precisam de esclarecimento**, não de interpretação conveniente pela equipe.

## Transformar regras em decisões de engenharia

Estas são **orientações de projeto Gaia**, sujeitas à confirmação do regulamento:

- **Estrutura:** reservar espaço para alça, bateria, eletrônica e sensores antes de fechar o CAD; medir altura e proporções na postura de inspeção; conferir envelope dos pés.
- **Eletrônica:** planejar bateria e computação embarcadas, proteção de alimentação e parada física. A bancada com USB/fonte externa é instrumento de desenvolvimento.
- **Sensores:** priorizar câmera passiva, IMU e estado das juntas na arquitetura inicial; antes de comprar LiDAR, ToF, câmera de profundidade ativa ou ultrassom, confirmar admissibilidade. Não alimentar a estimativa de orientação com magnetômetro sem verificar a regra.
- **Programação:** planejar percepção, decisão e marcha a bordo. Usar joystick/PC para bancada não demonstra autonomia competitiva. Separar mensagens de arbitragem de comandos manuais e tráfego de diagnóstico.
- **Simulação:** não usar pose perfeita do mundo ou posição verdadeira da bola como entrada da política competitiva. Esses dados servem para avaliar o erro, enquanto o algoritmo recebe sensores equivalentes aos permitidos.

## O OP3 resolve nossa conformidade?

Não automaticamente. Ele oferece uma referência útil, mas devemos medir e conferir a montagem Gaia. O laboratório OP3 está preso ao mundo por padrão, tem sensores ideais e limites de juntas do modelo original. Ele **não é uma arena oficial CBR** nem uma demonstração de elegibilidade.

Uma inconsistência concreta a revisar: o modelo OP3 de referência permite movimento amplo da cabeça, enquanto regulamentos podem limitar o mecanismo. A matriz de requisitos deve orientar URDF, limites de software e limites físicos — todos precisam concordar.

## Futebol: objetivos adicionais da autonomia

Depois de aprender as juntas e sensores, a equipe deve construir ensaios para:

1. Detectar bola, traves, linhas e adversários por visão.
2. Localizar o próprio robô e estimar a bola, com incerteza.
3. Entender os estados de jogo e penalidades do GameController.
4. Andar, parar, alinhar e chutar sem perder o equilíbrio.
5. Detectar queda e levantar de forma compatível com a montagem.
6. Cooperar dentro dos limites de comunicação e tolerar perda de rede.

Veja o [plano de autonomia](../simulacao/autonomia.md) e a [matriz de requisitos](matriz-requisitos.md).

## Próxima decisão da equipe

Confirmar com a organização **edição, subcategoria, documento vigente, retificações e critérios de inspeção**. Registrar a resposta junto do documento, sem tratar um e-mail informal antigo como regra permanente.

A pesquisa identificou a pendência; não foi enviado contato em nome da equipe.

[Inventário da pasta local e fontes](fontes.md).
