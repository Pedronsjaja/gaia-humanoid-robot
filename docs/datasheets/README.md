# Datasheets, manuais e esquemas

[Voltar ao README](../../README.md) Â· [InstalaÃ§Ã£o](../instalacao.md) Â· [Softwares](../softwares-e-drivers.md)

## Arquivos para baixar

As fontes foram consultadas em **20/09/2026**. Os arquivos abaixo sÃ£o cÃ³pias dos documentos distribuÃ­dos pela Hiwonder, preservadas sem ediÃ§Ã£o. A Hiwonder usa o termo **User Manual** para a documentaÃ§Ã£o das placas; nÃ£o sÃ£o datasheets de componentes eletrÃ´nicos.

| Equipamento | CÃ³pia neste repositÃ³rio | Original |
| --- | --- | --- |
| BusLinker V2.5 / TTL-USB | [Manual PDF â€” 24 pÃ¡ginas](buslinker-v2.5-manual.pdf) | [Servo Debug Board User Manual](https://drive.google.com/file/d/11u-8naW1CRMcVgWS1chedrtZbrX5WXIL/view) |
| BusLinker V2.5 / TTL-USB | [Esquema JPG](buslinker-v2.5-esquema.jpg) | [TTL Debugging Board.JPG](https://drive.google.com/file/d/1oa65bJ0ezJcTZdBPqjSolm7HpEHCe0Fz/view) |
| BusLinker V3.0 | [Manual PDF â€” 19 pÃ¡ginas](buslinker-v3.0-manual.pdf) | [BusLinker V3.0 User Manual](https://drive.google.com/file/d/1KueoY3lZ_0ceOeIImEY3QQmsVx9S1XFP/view) |
| BusLinker V3.0 | [Esquema PDF](buslinker-v3.0-esquema.pdf) | [BusLinker_v3.0.pdf](https://drive.google.com/file/d/1FLC4dy0MArV2XjpEt_cQ-ok0V5BSH92u/view) |
| Servo LX-225 | [Ficha tÃ©cnica oficial na web](https://www.hiwonder.com/products/lx-225) | [Pacote indicado pelo fabricante](https://drive.google.com/drive/folders/1rkb953c4ZGTqlhLmNy-2h8wiFlQwDI_h) |

A associaÃ§Ã£o do pacote TTL/USB Ã  **V2.5** vem da resposta do fabricante Ã  pergunta sobre essa revisÃ£o na [pÃ¡gina oficial da placa](https://www.hiwonder.com/products/hiwonder-ttl-usb-debugging-board). O PDF tem tÃ­tulo genÃ©rico, sem revisÃ£o na capa; confira a placa real antes de aplicar o esquema.

O PDF V3 disponÃ­vel no pacote Ã© uma ediÃ§Ã£o anterior Ã  [documentaÃ§Ã£o web V3](https://docs.hiwonder.com/projects/BusLinker/en/latest/docs/1_BusLinker_V3.0_Servo_Debugging_Board_User_Manual.html): o PDF se concentra em ServoStudio/servos magnÃ©ticos, enquanto a web inclui **Standard Servo PC Control Software Introduction**. Use essa seÃ§Ã£o web para as instruÃ§Ãµes do Bus Servo Terminal.

## ComparaÃ§Ã£o para esta bancada

| Item | V2.5 / TTL-USB | V3.0 |
| --- | --- | --- |
| Script do projeto | `buslinker_v2_5.py` | `buslinker_v3.py` |
| ComunicaÃ§Ã£o LX-225 neste cÃ³digo | 115200 baud | 115200 baud |
| Entrada da placa informada pela Hiwonder | 5â€“12,6 V na resposta comercial | 5â€“14 V no manual |
| ConexÃ£o com computador | USB, conforme conector da placa | USB-C |
| Diagrama e seleÃ§Ã£o de comunicaÃ§Ã£o | Conferir manual/esquema V2.5 | Conferir manual/esquema V3 |
| AlimentaÃ§Ã£o do conjunto com LX-225 | **6â€“8,4 V** | **6â€“8,4 V** |

A faixa da V2.5 estÃ¡ na [resposta oficial sobre tensÃ£o](https://www.hiwonder.com/products/hiwonder-ttl-usb-debugging-board); a V3 tem [especificaÃ§Ãµes no manual](buslinker-v3.0-manual.pdf). Os scripts implementam o mesmo protocolo LX-225. NÃ£o hÃ¡ mediÃ§Ã£o de desempenho comparativo entre as duas placas neste repositÃ³rio.

## ReferÃªncia rÃ¡pida do LX-225

| ParÃ¢metro | EspecificaÃ§Ã£o |
| --- | --- |
| TensÃ£o | 6â€“8,4 V |
| Torque anunciado | 25 kgÂ·cm a 7,4 V |
| Velocidade anunciada | 0,20 s/60Â° a 7,4 V |
| Corrente de travamento | 4 A |
| Peso e dimensÃµes | 63 g; 40 Ã— 20,14 Ã— 51,1 mm |
| ComunicaÃ§Ã£o | UART, 115200 baud |
| IDs | 0â€“253; padrÃ£o 1 |
| PosiÃ§Ã£o no protocolo | 0â€“1000 unidades â†’ 0â€“240Â° |
| Retorno de dados | PosiÃ§Ã£o, tensÃ£o e temperatura |

Fonte: [tabela tÃ©cnica Hiwonder LX-225](https://www.hiwonder.com/products/lx-225). A pÃ¡gina contÃ©m texto promocional com 270Â°, mas sua tabela e o controle por protocolo indicam **0â€“240Â°**, faixa adotada neste cÃ³digo. O torque mÃ¡ximo anunciado nÃ£o representa carga contÃ­nua validada da junta.

## Protocolo e procedÃªncia

- [Pacote oficial V2.5](https://drive.google.com/drive/folders/1PXvsWx50Fg76vtC3uHDibXKTKoKl4f26), vinculado pela pÃ¡gina TTL/USB.
- [Pacote oficial V3](https://drive.google.com/drive/folders/1yv1QZAjh_yLRWadZBb95nJ9dfWbHlKw_), vinculado pelo [Ã­ndice Hiwonder](https://docs.hiwonder.com/projects/BusLinker/en/latest/).
- [Protocolo Hiwonder/LewanSoul â€” espelho acadÃªmico do documento do fabricante](https://engineering.purdue.edu/477grp4/Team/journal/img%20-%20Juho/week7/servo%20bus%20protocol.pdf), referÃªncia jÃ¡ utilizada pelo projeto. NÃ£o confundir com o protocolo de servos magnÃ©ticos distribuÃ­do junto Ã  V3.
- [Registro de downloads e SHA-256](sources.json): URL, data, tamanho e hash de cada cÃ³pia.

A autoria dos manuais e esquemas permanece com o fabricante. Os nomes locais foram padronizados para facilitar links; os arquivos nÃ£o foram traduzidos nem modificados.
