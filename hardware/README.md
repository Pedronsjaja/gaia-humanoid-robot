# CAD do servo e suportes mecânicos

[Voltar ao README](../README.md) · [Softwares CAD](../docs/softwares-e-drivers.md) · [Dados do servo](../docs/datasheets/README.md)

## Qual arquivo baixar?

| Objetivo | Formato |
| --- | --- |
| Abrir a montagem do servo | SLDASM junto com todos os SLDPRT e imagens |
| Editar peça nativa | SLDPRT no SolidWorks ou IPT no Inventor |
| Adaptar os suportes em outro CAD | STEP/STP |
| Preparar impressão 3D | STL |
| Consultar aparência/dimensões | PNG ou AVIF |

No GitHub, abra o arquivo e use **Download raw file** quando disponível. Para a montagem, prefira **Code → Download ZIP** do repositório e extraia tudo. Não abra a montagem diretamente de dentro do ZIP.

## Servo LX-224 / LX-225

O mantenedor informou que o CAD LX-224 é o mesmo utilizado para LX-225 neste projeto. Essa equivalência é uma referência mecânica; confirme dimensões e fixações no servo real. Não implica equivalência elétrica com variantes HV.

Pasta: [cad/servo-lx224-lx225](cad/servo-lx224-lx225/).

| Arquivo | Conteúdo |
| --- | --- |
| [LX-224 Asembled.SLDASM](cad/servo-lx224-lx225/LX-224%20Asembled.SLDASM) | Montagem principal; grafia original preservada |
| [LX-224 Servo.SLDPRT](cad/servo-lx224-lx225/LX-224%20Servo.SLDPRT) | Modelo do corpo do servo |
| [FrontHub.SLDPRT](cad/servo-lx224-lx225/FrontHub.SLDPRT) | Peça frontal |
| [BackHub.SLDPRT](cad/servo-lx224-lx225/BackHub.SLDPRT) | Peça traseira |
| [Calcomania.png](cad/servo-lx224-lx225/Calcomania.png) | Imagem que acompanha o conjunto |
| [Especificaciones técnicas.png](cad/servo-lx224-lx225/Especificaciones%20t%C3%A9cnicas.png) | Referência visual original |
| [Dimensões LX-225](cad/servo-lx224-lx225/Lx_225/Dimens%C3%B5es_Lx225.avif) | Imagem dimensional fornecida |
| [Imagem LX-225](cad/servo-lx224-lx225/Lx_225/Lx_225.avif) | Referência visual |

Abra o SLDASM mantendo as peças na mesma pasta. Se o SolidWorks pedir referências, aponte para os SLDPRT locais. Não foi possível validar a abertura em SolidWorks nesta organização. Não há STEP/STL do corpo do servo no material fornecido.

## Suportes Gaia 3D

Origem: pasta fornecida **Suportes para o servo (Impressões 3D)/Gaia 3D**. As peças foram copiadas para o repositório; a pasta de origem foi mantida.

| Modelo | Editável Inventor | Intercâmbio CAD | Impressão |
| --- | --- | --- | --- |
| Bia Frame | [IPT](suportes/gaia-3d/IPT/Bia%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Bia%20Frame.stp) | [STL](suportes/gaia-3d/STL/Bia%20Frame.stl) |
| Long Frame | [IPT](suportes/gaia-3d/IPT/Long%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Long%20Frame.stp) | [STL](suportes/gaia-3d/STL/Long%20Frame.stl) |
| Medium Frame | [IPT](suportes/gaia-3d/IPT/Medium%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Medium%20Frame.stp) | [STL](suportes/gaia-3d/STL/Medium%20Frame.stl) |
| Short Frame | [IPT](suportes/gaia-3d/IPT/Short%20Frame.ipt) | [STEP](suportes/gaia-3d/STEP/Short%20Frame.stp) | [STL](suportes/gaia-3d/STL/Short%20Frame.stl) |
| Semaforo frame | [IPT](suportes/gaia-3d/IPT/Semaforo%20frame.ipt) | Não fornecido | Não fornecido |

## Outras peças LX-225

Origem: pasta fornecida **Partes do servo LX-225**. Disponíveis apenas em Inventor, sem conversão para STL/STEP:

- [Placa de Apoio](suportes/pecas-lx225/Placa%20de%20Apoio.ipt).
- [Suporte em L](suportes/pecas-lx225/Suporte%20em%20L.ipt).
- [Suporte em U Curto](suportes/pecas-lx225/Suporte%20em%20U%20Curto.ipt).
- [Suporte em U Inclinado](suportes/pecas-lx225/Suporte%20em%20U%20Inclinado.ipt).
- [Suporte em U Longo](suportes/pecas-lx225/Suporte%20em%20U%20Longo.ipt).
- [Suporte Multifuncional](suportes/pecas-lx225/Suporte%20Multifuncional.ipt).
- [Suporte Reto em formato linear](suportes/pecas-lx225/Suporte%20Reto%20em%20formato%20linear.ipt).
- [Viga em U](suportes/pecas-lx225/Viga%20em%20U.ipt).

## Preparar a impressão e montagem

1. Escolha um dos quatro STL disponíveis e abra no fatiador.
2. Confira as dimensões e a escala em milímetros: STL não registra unidade. Compare furos, espessura e encaixe com o STEP/IPT e o servo.
3. Escolha orientação que preserve resistência na direção de esforço e confira necessidade de suportes de impressão.
4. Defina material, paredes, preenchimento e temperatura de acordo com impressora e carga prevista. O projeto não inclui perfil de impressão validado.
5. Faça uma primeira peça para verificar encaixe e folgas. Confira passagem de cabos, comprimento dos parafusos e liberdade do eixo.
6. Só depois faça teste de bancada com pequenos deslocamentos e avance para a montagem da junta.

Não há ensaio estrutural documentado dos suportes. O torque nominal do servo não certifica a resistência de uma peça impressa.

## Organização e origem

Os nomes internos foram preservados. A pasta original **Servo Lx224_225 (CAD)** foi organizada em `cad/servo-lx224-lx225/`. Os dois conjuntos externos de suportes foram copiados sem alteração dos binários.

O [inventário SHA-256](manifest.json) permite conferir os arquivos e suas origens. A licença/autoria específica dos modelos não veio identificada nas pastas fornecidas; esta organização não atribui uma licença nova a arquivos de terceiros.
