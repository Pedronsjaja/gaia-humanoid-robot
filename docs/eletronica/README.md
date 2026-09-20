# Frente de eletrônica

[Início do Gaia](../../README.md) · [Como usar GitHub](../primeiros-passos-github.md)

A eletrônica deve entregar alimentação, comunicação e sensores confiáveis para a programação, com montagem e comportamento de falha documentados.

## Comece pela bancada

| Etapa | Guia |
| --- | --- |
| Conhecer placas/servo | [Manuais e esquemas V2.5/V3](../datasheets/README.md) |
| Instalar conversor USB | [Softwares e drivers](../softwares-e-drivers.md) |
| Ligar e consultar um servo | [Instalação e primeiro uso](../instalacao.md) |
| Investigar falta de resposta | [Diagnóstico](../solucao-de-problemas.md) |
| Montar painel de diagnóstico | [Joystick/OLED ESP32-S3](../joystick.md) |
| Escolher sensores para futebol | [Regulamento e pendências CBR](../competicao/README.md) |

A faixa usada na bancada LX-225 é **6–8,4 V**. Fonte, bateria, fusíveis/proteções e cabeamento precisam ser dimensionados para a carga do conjunto; a entrada máxima da BusLinker não altera a tensão admissível do servo. A integração do humanoide ainda exige seu diagrama completo.

## Entregas da frente

- Diagrama de alimentação, terra e sinal, com conectores/polaridades identificados.
- Lista de componentes e orçamento de corrente/energia.
- Mapa de IDs dos servos associado às juntas.
- Medição de tensão sob movimento e taxa de comunicação confiável.
- Plano de parada física e teste de perda de comunicação.
- Lista de sensores, posição e justificativa de admissibilidade na categoria.
- Registro de revisão de placa, firmware e cabeamento.

Computação e energia embarcadas fazem parte do objetivo de autonomia. Um computador conectado por USB à bancada ajuda no desenvolvimento, mas não substitui a arquitetura embarcada do jogador.

O firmware do joystick atual é diagnóstico: não existe ainda uma ligação funcional joystick → ROS 2 → LX-225. Confirme com programação os protocolos e com estrutura a fixação e proteção dos componentes.

Use a [matriz de requisitos](../competicao/matriz-requisitos.md) para acompanhar o que foi medido e o que falta.
