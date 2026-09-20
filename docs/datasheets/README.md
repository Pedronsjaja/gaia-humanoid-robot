# Datasheets, manuais e esquemas

[Voltar ao README](../../README.md) · [Instalação](../instalacao.md) · [Softwares](../softwares-e-drivers.md)

## Arquivos para baixar

As fontes foram consultadas em **20/09/2026**. Os arquivos abaixo são cópias dos documentos distribuídos pela Hiwonder, preservadas sem edição. A Hiwonder usa o termo **User Manual** para a documentação das placas; não são datasheets de componentes eletrônicos.

| Equipamento | Cópia neste repositório | Original |
| --- | --- | --- |
| BusLinker V2.5 / TTL-USB | [Manual PDF — 24 páginas](buslinker-v2.5-manual.pdf) | [Servo Debug Board User Manual](https://drive.google.com/file/d/11u-8naW1CRMcVgWS1chedrtZbrX5WXIL/view) |
| BusLinker V2.5 / TTL-USB | [Esquema JPG](buslinker-v2.5-esquema.jpg) | [TTL Debugging Board.JPG](https://drive.google.com/file/d/1oa65bJ0ezJcTZdBPqjSolm7HpEHCe0Fz/view) |
| BusLinker V3.0 | [Manual PDF — 19 páginas](buslinker-v3.0-manual.pdf) | [BusLinker V3.0 User Manual](https://drive.google.com/file/d/1KueoY3lZ_0ceOeIImEY3QQmsVx9S1XFP/view) |
| BusLinker V3.0 | [Esquema PDF](buslinker-v3.0-esquema.pdf) | [BusLinker_v3.0.pdf](https://drive.google.com/file/d/1FLC4dy0MArV2XjpEt_cQ-ok0V5BSH92u/view) |
| Servo LX-225 | [Ficha técnica oficial na web](https://www.hiwonder.com/products/lx-225) | [Pacote indicado pelo fabricante](https://drive.google.com/drive/folders/1rkb953c4ZGTqlhLmNy-2h8wiFlQwDI_h) |

A associação do pacote TTL/USB à **V2.5** vem da resposta do fabricante à pergunta sobre essa revisão na [página oficial da placa](https://www.hiwonder.com/products/hiwonder-ttl-usb-debugging-board). O PDF tem título genérico, sem revisão na capa; confira a placa real antes de aplicar o esquema.

O PDF V3 disponível no pacote é uma edição anterior à [documentação web V3](https://docs.hiwonder.com/projects/BusLinker/en/latest/docs/1_BusLinker_V3.0_Servo_Debugging_Board_User_Manual.html): o PDF se concentra em ServoStudio/servos magnéticos, enquanto a web inclui **Standard Servo PC Control Software Introduction**. Use essa seção web para as instruções do Bus Servo Terminal.

## Comparação para esta bancada

| Item | V2.5 / TTL-USB | V3.0 |
| --- | --- | --- |
| Script do projeto | `buslinker_v2_5.py` | `buslinker_v3.py` |
| Comunicação LX-225 neste código | 115200 baud | 115200 baud |
| Entrada da placa informada pela Hiwonder | 5–12,6 V na resposta comercial | 5–14 V no manual |
| Conexão com computador | USB, conforme conector da placa | USB-C |
| Diagrama e seleção de comunicação | Conferir manual/esquema V2.5 | Conferir manual/esquema V3 |
| Alimentação do conjunto com LX-225 | **6–8,4 V** | **6–8,4 V** |

A faixa da V2.5 está na [resposta oficial sobre tensão](https://www.hiwonder.com/products/hiwonder-ttl-usb-debugging-board); a V3 tem [especificações no manual](buslinker-v3.0-manual.pdf). Os scripts implementam o mesmo protocolo LX-225. Não há medição de desempenho comparativo entre as duas placas neste repositório.

## Referência rápida do LX-225

| Parâmetro | Especificação |
| --- | --- |
| Tensão | 6–8,4 V |
| Torque anunciado | 25 kg·cm a 7,4 V |
| Velocidade anunciada | 0,20 s/60° a 7,4 V |
| Corrente de travamento | 4 A |
| Peso e dimensões | 63 g; 40 × 20,14 × 51,1 mm |
| Comunicação | UART, 115200 baud |
| IDs | 0–253; padrão 1 |
| Posição no protocolo | 0–1000 unidades → 0–240° |
| Retorno de dados | Posição, tensão e temperatura |

Fonte: [tabela técnica Hiwonder LX-225](https://www.hiwonder.com/products/lx-225). A página contém texto promocional com 270°, mas sua tabela e o controle por protocolo indicam **0–240°**, faixa adotada neste código. O torque máximo anunciado não representa carga contínua validada da junta.

## Protocolo e procedência

- [Pacote oficial V2.5](https://drive.google.com/drive/folders/1PXvsWx50Fg76vtC3uHDibXKTKoKl4f26), vinculado pela página TTL/USB.
- [Pacote oficial V3](https://drive.google.com/drive/folders/1yv1QZAjh_yLRWadZBb95nJ9dfWbHlKw_), vinculado pelo [índice Hiwonder](https://docs.hiwonder.com/projects/BusLinker/en/latest/).
- [Protocolo Hiwonder/LewanSoul — espelho acadêmico do documento do fabricante](https://engineering.purdue.edu/477grp4/Team/journal/img%20-%20Juho/week7/servo%20bus%20protocol.pdf), referência já utilizada pelo projeto. Não confundir com o protocolo de servos magnéticos distribuído junto à V3.
- [Registro de downloads e SHA-256](sources.json): URL, data, tamanho e hash de cada cópia.

A autoria dos manuais e esquemas permanece com o fabricante. Os nomes locais foram padronizados para facilitar links; os arquivos não foram traduzidos nem modificados.
