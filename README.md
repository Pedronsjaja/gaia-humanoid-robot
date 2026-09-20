# Gaia — LX-225 e BusLinker V2.5 / V3

Bancada e biblioteca Python para o **servo Hiwonder LX-225** com **BusLinker V2.5 ou V3**: comunicação, consulta de posição/tensão/temperatura, movimentos de teste, gráficos, IDs e calibração.

## Comece aqui

1. Leia [como usar o GitHub](docs/primeiros-passos-github.md), se esta for sua primeira visita.
2. Siga a [instalação e primeiro teste](docs/instalacao.md), começando com um único servo.
3. Confira os [manuais e esquemas](docs/datasheets/README.md) da sua placa.
4. Use o [manual de comandos](docs/uso.md) e registre os resultados da bancada.

| Quero… | Abrir |
| --- | --- |
| Instalar Python, ligar a placa e identificar a porta | [Instalação](docs/instalacao.md) |
| Manuais V2.5/V3 e ficha LX-225 | [Documentação técnica](docs/datasheets/README.md) |
| Software Hiwonder e driver USB | [Softwares e drivers](docs/softwares-e-drivers.md) |
| Consultar sensores, mover ou calibrar | [Comandos Python](docs/uso.md) |
| Resolver erros | [Solução de problemas](docs/solucao-de-problemas.md) |
| Conferir alimentação e barramento | [Eletrônica do LX-225](docs/eletronica/README.md) |
| Reutilizar a biblioteca no robô | [Interface dos atuadores](docs/gaia_lx225.md) |
| Baixar CAD do servo e suportes | [Catálogo no repositório de estrutura](https://github.com/Pedronsjaja/gaia-humanoid-structure/blob/main/hardware/README.md) |

## Qual programa usar?

| Placa | Programa independente | Classe |
| --- | --- | --- |
| BusLinker V2.5 | [buslinker_v2_5.py](buslinker_v2_5.py) | `BusLinkerV2_5` |
| BusLinker V3 | [buslinker_v3.py](buslinker_v3.py) | `BusLinkerV3` |

Instale as dependências de [requirements.txt](requirements.txt). Os dois programas usam o protocolo LX-225 a 115200 baud. Confira o comando da sua revisão no tutorial; V3 não significa compatibilidade com qualquer protocolo de servo.

Comece consultando o estado. Antes de mover, confirme ID, alimentação, limites e percurso mecânico. A referência elétrica e as diferenças entre tensão da placa e do servo estão nos [manuais](docs/datasheets/README.md).

## Organização

```text
buslinker_v2_5.py       Programa completo V2.5
buslinker_v3.py         Programa completo V3
servo_testbench.py     Comunicação compartilhada
bench_tools.py         Gráficos, IDs e calibração
test_servos.py         Interface da bancada
docs/                  Instalação, uso, manuais e diagnóstico
tests/                 Testes com serial simulada
tools/                 Diagnóstico e geração dos programas
```

Para desenvolver, altere as fontes compartilhadas e gere novamente os programas independentes com `python tools/build_standalone.py`.

```powershell
python -m unittest discover -s tests -v
```

Os testes de software não certificam a montagem elétrica ou mecânica. Corrente e torque não são medidos por este driver; a velocidade exibida é estimada entre leituras.

## Repositórios da equipe Gaia

| Preciso de… | Repositório |
| --- | --- |
| Servo LX-225, BusLinker, drivers e testes de bancada | [LX-225 / BusLinker](https://github.com/Pedronsjaja/gaia-lx225-buslinker) |
| Gazebo, OP3, ROS 2 e autonomia | [Simulação](https://github.com/Pedronsjaja/gaia-humanoid-simulation) |
| CAD, suportes, montagem e requisitos físicos da CBR | [Estrutura](https://github.com/Pedronsjaja/gaia-humanoid-structure) |
| Instalar Ubuntu 24.04 e ROS 2 Jazzy | [Ambiente Linux / ROS 2](https://github.com/Pedronsjaja/gaia-ros2-ubuntu24) |

Cada repositório tem seus próprios arquivos, Issues e histórico. Abra dúvidas na área correspondente; inclua links quando uma mudança depender de outra área.

O antigo repositório `gaia-humanoid-robot` foi renomeado para este endereço. Simulação e arquivos mecânicos passaram para os repositórios acima; o histórico anterior permanece preservado.
