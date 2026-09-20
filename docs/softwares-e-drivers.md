# Softwares e drivers

[Voltar ao README](../README.md) · [Instalação](instalacao.md) · [Manuais](datasheets/README.md)

## O que instalar

| Componente | Para que serve | Necessidade |
| --- | --- | --- |
| Python + pyserial | Executar scripts e acessar a serial | Para a bancada Python |
| matplotlib | Gerar gráficos | Instalado por requirements.txt |
| CH341SER da WCH | Reconhecer conversores USB CH340/CH341 | Se o sistema não reconhecer a placa |
| Bus Servo Terminal | Consultar/configurar servos padrão com interface gráfica | Opcional para usar Python |
| ServoStudio | Ferramenta citada no manual V3 para servos magnéticos compatíveis | Não é requisito do LX-225 |
| VS Code | Editor e terminal | Opcional |
| PlatformIO | Compilar/gravar diagnóstico do joystick | Só para o firmware ESP32-S3 |

**V2.5/V3.0 identificam placas. V2.3 identifica uma versão do Bus Servo Terminal.** Os números não precisam coincidir. Para LX-225, use comunicação a **115200 baud**, conforme [especificação do servo](https://www.hiwonder.com/products/lx-225); não copie os exemplos a 1 Mbaud dos servos magnéticos.

## Downloads oficiais

- [Python](https://www.python.org/downloads/) e [VS Code](https://code.visualstudio.com/).
- [WCH CH341SER — Windows e links para outras plataformas](https://www.wch-ic.com/downloads/CH341SER.EXE.html?type=en).
- [Pacote de software/driver V2.5](https://drive.google.com/drive/folders/1XJZ8-vH_Ird9maY-G4CtM7BUNHgw-TGg): pastas BusLinker Debug Board Drive e BusLinker Debug Board Software.
- [Pacote de softwares V3](https://drive.google.com/drive/folders/1pvLu30CD031MmmyniB1jsr8tejrHD9rp).
- [Bus Servo Terminal setup V2.3.exe — arquivo no pacote oficial V3](https://drive.google.com/file/d/14IyadBqcuB1EVzPrle2UwC0VONXBObUK/view).
- [PlatformIO para VS Code](https://platformio.org/install/ide?install=vscode), usado pelo [guia do joystick](joystick.md).

Os pacotes são vinculados pelo [site Hiwonder da placa TTL/USB](https://www.hiwonder.com/products/hiwonder-ttl-usb-debugging-board) e pela [documentação BusLinker V3](https://docs.hiwonder.com/projects/BusLinker/en/latest/). Instaladores permanecem na distribuição oficial; não são executados automaticamente por este repositório.

## Instalar CH341SER no Windows

1. Confirme no Gerenciador de Dispositivos que o dispositivo corresponde a um conversor CH340/CH341.
2. Baixe o pacote WCH acima ou o driver contido no pacote oficial da placa.
3. Execute o instalador e escolha **INSTALL**, seguindo os avisos do Windows.
4. Reconecte o USB e confira **Portas (COM e LPT)**.
5. Anote a porta, normalmente identificada como USB-SERIAL CH340.

Esses passos seguem o [manual V2.5](datasheets/buslinker-v2.5-manual.pdf). Para outro chip USB, identifique o componente antes de escolher seu driver. Instalar `pyserial` não instala o driver USB do sistema.

## Primeiro uso do Bus Servo Terminal

1. Instale o Bus Servo Terminal pelo pacote oficial.
2. Conecte somente um LX-225 e use alimentação apropriada.
3. Abra o software, selecione a COM e configure 115200 baud.
4. Abra a conexão e consulte o ID conhecido; use a busca disponível na sua versão se necessário.
5. Confirme posição, tensão e temperatura antes de alterar parâmetros ou mover.
6. Feche a conexão e o programa antes de iniciar Python.

Para posições dos jumpers e telas, consulte os [manuais locais](datasheets/README.md). O [manual V3](https://docs.hiwonder.com/projects/BusLinker/en/latest/docs/1_BusLinker_V3.0_Servo_Debugging_Board_User_Manual.html) separa servos padrão de servos magnéticos: use a seção **Standard Servo** como referência do software para LX-225. Não grave firmware de outro modelo no servo.

## Abrir os arquivos mecânicos

| Formato | Uso |
| --- | --- |
| SLDASM + SLDPRT | Montagem e peças nativas SolidWorks |
| IPT | Peças nativas Autodesk Inventor |
| STEP/STP | Intercâmbio CAD; pode ser aberto em ferramentas como FreeCAD |
| STL | Malha para fatiador de impressão 3D; confira escala e dimensões |
| PNG/AVIF | Referências visuais; não são modelos CAD |

Consulte [SolidWorks](https://www.solidworks.com/), [Inventor](https://www.autodesk.com/products/inventor/overview) e [FreeCAD](https://www.freecad.org/). A versão de gravação dos arquivos nativos não foi identificada. Não foi feita conversão automática de formatos. Veja o [catálogo](../hardware/README.md).
