# Frente de estrutura mecânica

[Início do Gaia](../../README.md) · [Como usar GitHub](../primeiros-passos-github.md)

Esta frente transforma a referência OP3 em uma montagem Gaia fabricável, com dimensões, rigidez, massas e manutenção documentadas.

## Comece aqui

1. Abra o [catálogo CAD e suportes](../../hardware/README.md).
2. Confira os [requisitos CBR Humanoid](../competicao/README.md) antes de fechar altura, pés e cabeça.
3. Estude a [montagem OP3](https://emanual.robotis.com/docs/en/platform/op3/hardware/#hardware).
4. Siga [CAD → modelo Gaia](../simulacao/modelo-gaia.md) para entregar dados à simulação.

| Preciso… | Onde |
| --- | --- |
| Ver a montagem do servo | [SolidWorks LX-224/LX-225](../../hardware/cad/servo-lx224-lx225/) |
| Imprimir suportes disponíveis | [STL Gaia 3D](../../hardware/suportes/gaia-3d/STL/) |
| Adaptar suporte em outro CAD | [STEP](../../hardware/suportes/gaia-3d/STEP/) |
| Editar peças nativas | [IPT Gaia 3D](../../hardware/suportes/gaia-3d/IPT/) e [peças LX-225](../../hardware/suportes/pecas-lx225/) |

## Entrega por conjunto mecânico

Documente versão, unidades, massa, material, centro de massa, parafusos, folgas, posição dos eixos e limites. Para peças impressas, registre impressora/material/orientação/parâmetros e resultado do encaixe; não trate um STL como perfil de impressão pronto.

Mantenha montagem nativa e suas referências juntas. Para compartilhar uma alteração, exporte STEP quando possível e STL quando houver finalidade de impressão; confira que as exportações correspondem à mesma revisão.

A estrutura ainda deve prever fixação da bateria e computador, passagem de cabos, alça, acesso à parada e proteção de componentes nas quedas. Combine com eletrônica a massa/disposição dos componentes e com programação o sentido positivo das juntas.

Use a [matriz de requisitos](../competicao/matriz-requisitos.md) para registrar medições e pendências.
