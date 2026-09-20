# Eletrônica da bancada LX-225

[Início](../../README.md)

Esta área cobre alimentação, BusLinker, barramento e identificação dos servos LX-225.

| Etapa | Guia |
| --- | --- |
| Conferir placa e servo | [Manuais e esquemas](../datasheets/README.md) |
| Instalar conversor USB | [Softwares e drivers](../softwares-e-drivers.md) |
| Conectar e consultar um servo | [Instalação](../instalacao.md) |
| Investigar falta de resposta | [Diagnóstico](../solucao-de-problemas.md) |
| Definir IDs e calibração | [Uso](../uso.md) |

Confira a tensão admissível do servo, polaridade, terra comum e conectores antes de ligar. Dimensione alimentação e cabos para os movimentos previstos e meça a tensão sob carga. A tensão máxima da placa não aumenta a tensão permitida pelo LX-225.

Registre revisão da placa, fonte, IDs, cabeamento e resultado do ensaio. A troca de ID deve ser feita com um único servo conectado.

Para CAD, fixação, painel auxiliar e integração física do humanoide, use o [repositório de estrutura](https://github.com/Pedronsjaja/gaia-humanoid-structure). Para sensores virtuais e ROS 2, use o [repositório de simulação](https://github.com/Pedronsjaja/gaia-humanoid-simulation).
