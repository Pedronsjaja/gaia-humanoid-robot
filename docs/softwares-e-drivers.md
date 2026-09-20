# Softwares e drivers

[Voltar ao README](../README.md) Â· [InstalaÃ§Ã£o](instalacao.md) Â· [Manuais](datasheets/README.md)

## O que instalar

| Componente | Para que serve | Necessidade |
| --- | --- | --- |
| Python + pyserial | Executar scripts e acessar a serial | Para a bancada Python |
| matplotlib | Gerar grÃ¡ficos | Instalado por requirements.txt |
| CH341SER da WCH | Reconhecer conversores USB CH340/CH341 | Se o sistema nÃ£o reconhecer a placa |
| Bus Servo Terminal | Consultar/configurar servos padrÃ£o com interface grÃ¡fica | Opcional para usar Python |
| ServoStudio | Ferramenta citada no manual V3 para servos magnÃ©ticos compatÃ­veis | NÃ£o Ã© requisito do LX-225 |
| VS Code | Editor e terminal | Opcional |
| PlatformIO | Compilar/gravar diagnÃ³stico do joystick | SÃ³ para o firmware ESP32-S3 |

**V2.5/V3.0 identificam placas. V2.3 identifica uma versÃ£o do Bus Servo Terminal.** Os nÃºmeros nÃ£o precisam coincidir. Para LX-225, use comunicaÃ§Ã£o a **115200 baud**, conforme [especificaÃ§Ã£o do servo](https://www.hiwonder.com/products/lx-225); nÃ£o copie os exemplos a 1 Mbaud dos servos magnÃ©ticos.

## Downloads oficiais

- [Python](https://www.python.org/downloads/) e [VS Code](https://code.visualstudio.com/).
- [WCH CH341SER â€” Windows e links para outras plataformas](https://www.wch-ic.com/downloads/CH341SER.EXE.html?type=en).
- [Pacote de software/driver V2.5](https://drive.google.com/drive/folders/1XJZ8-vH_Ird9maY-G4CtM7BUNHgw-TGg): pastas BusLinker Debug Board Drive e BusLinker Debug Board Software.
- [Pacote de softwares V3](https://drive.google.com/drive/folders/1pvLu30CD031MmmyniB1jsr8tejrHD9rp).
- [Bus Servo Terminal setup V2.3.exe â€” arquivo no pacote oficial V3](https://drive.google.com/file/d/14IyadBqcuB1EVzPrle2UwC0VONXBObUK/view).
- [PlatformIO para VS Code](https://platformio.org/install/ide?install=vscode), usado pelo [guia do joystick](joystick.md).

Os pacotes sÃ£o vinculados pelo [site Hiwonder da placa TTL/USB](https://www.hiwonder.com/products/hiwonder-ttl-usb-debugging-board) e pela [documentaÃ§Ã£o BusLinker V3](https://docs.hiwonder.com/projects/BusLinker/en/latest/). Instaladores permanecem na distribuiÃ§Ã£o oficial; nÃ£o sÃ£o executados automaticamente por este repositÃ³rio.

## Instalar CH341SER no Windows

1. Confirme no Gerenciador de Dispositivos que o dispositivo corresponde a um conversor CH340/CH341.
2. Baixe o pacote WCH acima ou o driver contido no pacote oficial da placa.
3. Execute o instalador e escolha **INSTALL**, seguindo os avisos do Windows.
4. Reconecte o USB e confira **Portas (COM e LPT)**.
5. Anote a porta, normalmente identificada como USB-SERIAL CH340.

Esses passos seguem o [manual V2.5](datasheets/buslinker-v2.5-manual.pdf). Para outro chip USB, identifique o componente antes de escolher seu driver. Instalar `pyserial` nÃ£o instala o driver USB do sistema.

## Primeiro uso do Bus Servo Terminal

1. Instale o Bus Servo Terminal pelo pacote oficial.
2. Conecte somente um LX-225 e use alimentaÃ§Ã£o apropriada.
3. Abra o software, selecione a COM e configure 115200 baud.
4. Abra a conexÃ£o e consulte o ID conhecido; use a busca disponÃ­vel na sua versÃ£o se necessÃ¡rio.
5. Confirme posiÃ§Ã£o, tensÃ£o e temperatura antes de alterar parÃ¢metros ou mover.
6. Feche a conexÃ£o e o programa antes de iniciar Python.

Para posiÃ§Ãµes dos jumpers e telas, consulte os [manuais locais](datasheets/README.md). O [manual V3](https://docs.hiwonder.com/projects/BusLinker/en/latest/docs/1_BusLinker_V3.0_Servo_Debugging_Board_User_Manual.html) separa servos padrÃ£o de servos magnÃ©ticos: use a seÃ§Ã£o **Standard Servo** como referÃªncia do software para LX-225. NÃ£o grave firmware de outro modelo no servo.

## Abrir os arquivos mecÃ¢nicos

| Formato | Uso |
| --- | --- |
| SLDASM + SLDPRT | Montagem e peÃ§as nativas SolidWorks |
| IPT | PeÃ§as nativas Autodesk Inventor |
| STEP/STP | IntercÃ¢mbio CAD; pode ser aberto em ferramentas como FreeCAD |
| STL | Malha para fatiador de impressÃ£o 3D; confira escala e dimensÃµes |
| PNG/AVIF | ReferÃªncias visuais; nÃ£o sÃ£o modelos CAD |

Consulte [SolidWorks](https://www.solidworks.com/), [Inventor](https://www.autodesk.com/products/inventor/overview) e [FreeCAD](https://www.freecad.org/). A versÃ£o de gravaÃ§Ã£o dos arquivos nativos nÃ£o foi identificada. NÃ£o foi feita conversÃ£o automÃ¡tica de formatos. Veja o [catÃ¡logo](../hardware/README.md).
