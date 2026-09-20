# Registro de validação do laboratório

[Índice](README.md) · [Versões e fontes](referencias.md)

## Verificado em 20/09/2026

No Windows do mantenedor, sem ROS/Gazebo instalado:

- Expansão do Xacro da revisão ROBOTIS fixada no manifesto.
- Cinco testes do adaptador: preservação das juntas/geometria/inércias; base presa/livre; correspondência das 20 juntas e controladores; rejeição de modelo alterado/duplicado; sensores e tópicos da ponte.
- Análise de sintaxe Python e leitura de configurações XML/YAML.
- 47 testes da bancada Python com serial simulada.
- Verificação dos destinos dos links relativos Markdown.

## Integração Linux aprovada

A [execução 35541058398](https://github.com/Pedronsjaja/gaia-humanoid-robot/actions/runs/35541058398) passou em **20/09/2026**, na revisão Gaia `e2e3195`, com Ubuntu 24.04, contêiner ROS Jazzy e renderização Mesa por software, sem janela.

Resultados observados:

- Dependências resolvidas por rosdep e dois pacotes compilados.
- Cinco testes do modelo aprovados também em Linux.
- Gazebo iniciado e OP3 inserido com base presa.
- Recebidos relógio, estado das 20 juntas, imagem 320 × 240, CameraInfo e IMU.
- Conferidos os identificadores de frame da imagem e da IMU.
- Controlador de trajetória ativo antes do envio.
- `head_pan` chegou a 0,15 rad e retornou a zero, com tolerância de 0,025 rad no teste.

O [teste de integração](../../ros2/gaia_op3_sim/test/smoke_sim.py) e o [workflow](../../.github/workflows/simulation.yml) ficam versionados. Receber uma imagem não comprova enquadramento, aparência das malhas ou qualidade da visão. Esse ensaio também não valida equilíbrio, base livre ou atuação real LX-225.

As novas execuções podem ser acompanhadas em [Actions](https://github.com/Pedronsjaja/gaia-humanoid-robot/actions/workflows/simulation.yml).


## Ensaio pendente no computador da equipe

Execute o [tutorial](instalacao-e-laboratorio.md) e anexe à Issue uma ficha:

| Campo | Preencher após o ensaio |
| --- | --- |
| Pessoa/data | — |
| CPU, RAM, GPU/driver | — |
| Ubuntu e ROS | — |
| Dual boot ou VM/versão | — |
| Commit Gaia e revisão OP3 | — |
| Compilação e logs | — |
| Modelo visível e base presa | — |
| Controladores ativos e 20 juntas | — |
| head_pan atinge 0,15 rad e retorna | — |
| Imagem, CameraInfo e frames coerentes | — |
| IMU em repouso e durante movimento | — |
| Taxas e fator de tempo real observados | — |
| Encerramento sem processos residuais | — |

Não registre “aprovado” apenas porque a janela abriu. Compare alvos e leituras; confira a direção da câmera e as malhas. Marcha, equilíbrio, modelo físico LX-225 e futebol autônomo exigem ensaios adicionais.
