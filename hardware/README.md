# CAD do servo e suportes mecÃ¢nicos

[Voltar ao README](../README.md) Â· [Softwares CAD](../docs/softwares-e-drivers.md) Â· [Dados do servo](../docs/datasheets/README.md)

## Qual arquivo baixar?

| Objetivo | Formato |
| --- | --- |
| Abrir a montagem do servo | SLDASM junto com todos os SLDPRT e imagens |
| Editar peÃ§a nativa | SLDPRT no SolidWorks ou IPT no Inventor |
| Adaptar os suportes em outro CAD | STEP/STP |
| Preparar impressÃ£o 3D | STL |
| Consultar aparÃªncia/dimensÃµes | PNG ou AVIF |

No GitHub, abra o arquivo e use **Download raw file** quando disponÃ­vel. Para a montagem, prefira **Code â†’ Download ZIP** do repositÃ³rio e extraia tudo. NÃ£o abra a montagem diretamente de dentro do ZIP.

## Servo LX-224 / LX-225

O mantenedor informou que o CAD LX-224 Ã© o mesmo utilizado para LX-225 neste projeto. Essa equivalÃªncia Ã© uma referÃªncia mecÃ¢nica; confirme dimensÃµes e fixaÃ§Ãµes no servo real. NÃ£o implica equivalÃªncia elÃ©trica com variantes HV.

Pasta: [cad/servo-lx224-lx225](cad/servo-lx224-lx225/).

| Arquivo | ConteÃºdo |
| --- | --- |
| [LX-224 Asembled.SLDASM](cad/servo-lx224-lx225/LX-224%20Asembled.SLDASM) | Montagem principal; grafia original preservada |
| [LX-224 Servo.SLDPRT](cad/servo-lx224-lx225/LX-224%20Servo.SLDPRT) | Modelo do corpo do servo |
| [FrontHub.SLDPRT](cad/servo-lx224-lx225/FrontHub.SLDPRT) | PeÃ§a frontal |
| [BackHub.SLDPRT](cad/servo-lx224-lx225/BackHub.SLDPRT) | PeÃ§a traseira |
| [Calcomania.png](cad/servo-lx224-lx225/Calcomania.png) | Imagem que acompanha o conjunto |
| [Especificaciones tÃ©cnicas.png](cad/servo-lx224-lx225/Especificaciones%20t%C3%A9cnicas.png) | ReferÃªncia visual original |
| [DimensÃµes LX-225](cad/servo-lx224-lx225/Lx_225/Dimens%C3%B5es_Lx225.avif) | Imagem dimensional fornecida |
| [Imagem LX-225](cad/servo-lx224-lx225/Lx_225/Lx_225.avif) | ReferÃªncia visual |

Abra o SLDASM mantendo as peÃ§as na mesma pasta. Se o SolidWorks pedir referÃªncias, aponte para os SLDPRT locais. NÃ£o foi possÃ­vel validar a abertura em SolidWorks nesta organizaÃ§Ã£o. NÃ£o hÃ¡ STEP/STL do corpo do servo no material fornecido.

## Suportes Gaia 3D

Origem: pasta fornecida **Suportes para o servo (ImpressÃµes 3D)/Gaia 3D**. As peÃ§as foram copiadas para o repositÃ³rio; a pasta de origem foi mantida.

| Modelo | EditÃ¡vel Inventor | IntercÃ¢mbio CAD | ImpressÃ£o |
| --- | --- | --- | --- |
| Bia Frame | [IPT](suportes/gaia-3d/IPT/Bia%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Bia%20Frame.stp) | [STL](suportes/gaia-3d/STL/Bia%20Frame.stl) |
| Long Frame | [IPT](suportes/gaia-3d/IPT/Long%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Long%20Frame.stp) | [STL](suportes/gaia-3d/STL/Long%20Frame.stl) |
| Medium Frame | [IPT](suportes/gaia-3d/IPT/Medium%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Medium%20Frame.stp) | [STL](suportes/gaia-3d/STL/Medium%20Frame.stl) |
| Short Frame | [IPT](suportes/gaia-3d/IPT/Short%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Short%20Frame.stp) | [STL](suportes/gaia-3d/STL/Short%20Frame.stl) |
| Semaforo frame | [IPT](suportes/gaia-3d/IPT/Semaforo%20frame.ipt) | NÃ£o fornecido | NÃ£o fornecido |

## Outras peÃ§as LX-225

Origem: pasta fornecida **Partes do servo LX-225**. DisponÃ­veis apenas em Inventor, sem conversÃ£o para STL/STEP:

- [Placa de Apoio](suportes/pecas-lx225/Placa%20de%20Apoio.ipt).
- [Suporte em L](suportes/pecas-lx225/Suporte%20em%20L.ipt).
- [Suporte em U Curto](suportes/pecas-lx225/Suporte%20em%20U%20Curto.ipt).
- [Suporte em U Inclinado](suportes/pecas-lx225/Suporte%20em%20U%20Inclinado.ipt).
- [Suporte em U Longo](suportes/pecas-lx225/Suporte%20em%20U%20Longo.ipt).
- [Suporte Multifuncional](suportes/pecas-lx225/Suporte%20Multifuncional.ipt).
- [Suporte Reto em formato linear](suportes/pecas-lx225/Suporte%20Reto%20em%20formato%20linear.ipt).
- [Viga em U](suportes/pecas-lx225/Viga%20em%20U.ipt).

## Preparar a impressÃ£o e montagem

1. Escolha um dos quatro STL disponÃ­veis e abra no fatiador.
2. Confira as dimensÃµes e a escala em milÃ­metros: STL nÃ£o registra unidade. Compare furos, espessura e encaixe com o STEP/IPT e o servo.
3. Escolha orientaÃ§Ã£o que preserve resistÃªncia na direÃ§Ã£o de esforÃ§o e confira necessidade de suportes de impressÃ£o.
4. Defina material, paredes, preenchimento e temperatura de acordo com impressora e carga prevista. O projeto nÃ£o inclui perfil de impressÃ£o validado.
5. FaÃ§a uma primeira peÃ§a para verificar encaixe e folgas. Confira passagem de cabos, comprimento dos parafusos e liberdade do eixo.
6. SÃ³ depois faÃ§a teste de bancada com pequenos deslocamentos e avance para a montagem da junta.

NÃ£o hÃ¡ ensaio estrutural documentado dos suportes. O torque nominal do servo nÃ£o certifica a resistÃªncia de uma peÃ§a impressa.

## OrganizaÃ§Ã£o e origem

Os nomes internos foram preservados. A pasta original **Servo Lx224_225 (CAD)** foi organizada em `cad/servo-lx224-lx225/`. Os dois conjuntos externos de suportes foram copiados sem alteraÃ§Ã£o dos binÃ¡rios.

O [inventÃ¡rio SHA-256](manifest.json) permite conferir os arquivos e suas origens. A licenÃ§a/autoria especÃ­fica dos modelos nÃ£o veio identificada nas pastas fornecidas; esta organizaÃ§Ã£o nÃ£o atribui uma licenÃ§a nova a arquivos de terceiros.
