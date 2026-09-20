# Frente de programação

[Início do Gaia](../../README.md) · [Como usar GitHub](../primeiros-passos-github.md)

A programação liga os objetivos do robô aos sensores e atuadores. Comece pelo ambiente e por um teste pequeno que possa ser observado.

| Ordem | Material | O que entregar |
| --- | --- | --- |
| 1 | [Ubuntu 24.04 e ROS 2 Jazzy](https://github.com/Pedronsjaja/gaia-ros2-ubuntu24) | Talker/listener no seu computador |
| 2 | [Laboratório OP3](../simulacao/instalacao-e-laboratorio.md) | Modelo, juntas e sensores virtuais |
| 3 | [Comandos LX-225](../uso.md) e [instalação da bancada](../instalacao.md) | Leitura de um servo real, junto da eletrônica |
| 4 | [Modelo Gaia](../simulacao/modelo-gaia.md) | Descrição da junta validada pela estrutura |
| 5 | [Autonomia](../simulacao/autonomia.md) | Percepção, estimativa, decisão e controle |
| 6 | [CBR Humanoid](../competicao/README.md) | Requisitos de futebol e arbitragem rastreáveis |

## Onde fica o código?

| Caminho | Função |
| --- | --- |
| [ros2/gaia_op3_sim](../../ros2/gaia_op3_sim/) | Laboratório do simulador |
| [simulation/op3.repos](../../simulation/op3.repos) | Revisão do modelo oficial a baixar |
| [buslinker_v2_5.py](../../buslinker_v2_5.py) / [buslinker_v3.py](../../buslinker_v3.py) | Programas completos de bancada |
| [servo_testbench.py](../../servo_testbench.py) | Fonte compartilhada de comunicação LX-225 |
| [bench_tools.py](../../bench_tools.py) | Gráficos, IDs e calibração |
| [tests](../../tests/) | Testes de bancada sem hardware |
| [tools](../../tools/) | Diagnóstico e geração dos programas completos |
| [firmware](../../firmware/) | Diagnóstico ESP32-S3 de joystick/OLED |

Os arquivos autônomos da BusLinker são gerados: altere as fontes compartilhadas e rode o gerador. Não mantenha versões divergentes manualmente.

## Como trabalhar com as outras frentes

Peça à estrutura nomes, eixos, limites e zero de cada junta. Peça à eletrônica alimentação, IDs, taxa de leitura confiável, sensores e estados de falha. Não assuma que um nome no URDF já corresponde ao servo físico.

Cada mudança deve explicar problema, comportamento esperado, teste feito e limitação conhecida. Use uma branch e abra um Pull Request; veja o [guia GitHub](../primeiros-passos-github.md).
