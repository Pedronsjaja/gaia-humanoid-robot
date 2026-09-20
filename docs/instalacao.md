# InstalaÃ§Ã£o e primeiro uso

[Voltar ao README](../README.md) Â· [Downloads](softwares-e-drivers.md) Â· [Problemas](solucao-de-problemas.md)

## 1. Separe e conecte o material

| Material | Conferir |
| --- | --- |
| BusLinker V2.5 ou V3.0 | RevisÃ£o impressa na placa e seleÃ§Ã£o de comunicaÃ§Ã£o |
| Um LX-225 e cabo de servo | Cabo Ã­ntegro e eixo com percurso livre |
| Fonte externa | 6â€“8,4 V no LX-225, polaridade e corrente adequadas |
| USB de dados | Conector da revisÃ£o; V3 usa USB-C |
| Computador | Python e porta USB disponÃ­veis |

FaÃ§a as conexÃµes com a fonte desligada. Confira alimentaÃ§Ã£o, terra comum e sinal pelos rÃ³tulos e [diagramas da revisÃ£o](datasheets/README.md), nÃ£o apenas pela cor do cabo. A fonte alimenta os servos; nÃ£o use sÃ³ o USB como alimentaÃ§Ã£o de potÃªncia.

Na V3, o manual de servos padrÃ£o indica a seleÃ§Ã£o **Servo/USB**. Veja a figura do manual antes de colocar os jumpers. NÃ£o copie posiÃ§Ãµes fÃ­sicas entre revisÃµes. Os exemplos com 11,1/12 V do manual sÃ£o para outros servos: **nÃ£o aplique essa tensÃ£o ao LX-225**.

## 2. Instale Python e baixe o projeto

Baixe Python no [site oficial](https://www.python.org/downloads/). O cÃ³digo exige Python 3.9 ou superior; a verificaÃ§Ã£o local deste trabalho usa Python 3.13. Se o instalador oferecer inclusÃ£o no PATH, habilite-a. Abra um terminal novo:

```powershell
python --version
```

No GitHub, use **Code â†’ Download ZIP** e extraia tudo. Outra opÃ§Ã£o Ã© copiar a URL HTTPS em **Code** e executar `git clone URL_COPIADA`. Abra a pasta no VS Code ou terminal. Ela deve conter `README.md` e `requirements.txt`.

## 3. Prepare o ambiente no Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import serial, matplotlib; from servo_testbench import LX225Bus; print('Instalacao OK')"
```

O resultado esperado Ã© `Instalacao OK`. `pyserial` acessa a serial e `matplotlib` gera os grÃ¡ficos.

Para executar os exemplos curtos do manual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativaÃ§Ã£o, use `.\.venv\Scripts\python.exe` no lugar de `python`; nÃ£o Ã© necessÃ¡rio mudar a polÃ­tica do sistema. No VS Code, escolha **Python: Select Interpreter** e selecione o Python de `.venv`.

## 4. Identifique a porta USB

1. Conecte a placa com um cabo USB de dados.
2. Abra **Gerenciador de Dispositivos â†’ Portas (COM e LPT)**.
3. Se o conversor CH340/CH341 estiver sem driver, siga [CH341SER](softwares-e-drivers.md). Se jÃ¡ funcionar, nÃ£o precisa reinstalar.
4. Anote a COM. Desconectar e reconectar o USB ajuda a identificar a entrada correspondente.

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v
```

`COM7` Ã© apenas exemplo; substitua nos comandos. A presenÃ§a da COM confirma o conversor USB, nÃ£o a comunicaÃ§Ã£o com o servo.

## 5. FaÃ§a a primeira leitura

Conecte um Ãºnico servo com a fonte desligada, confira a seleÃ§Ã£o USB e ligue a fonte. Feche Bus Servo Terminal, ServoStudio e monitores seriais que possam ocupar a porta.

```powershell
.\.venv\Scripts\python.exe buslinker_v3.py --port COM7 --scan
```

Na V2.5, use `buslinker_v2_5.py`. A busca percorre 0â€“253, pode levar cerca de 12 segundos e nÃ£o altera configuraÃ§Ãµes. Espere um ID com posiÃ§Ã£o, tensÃ£o e temperatura vÃ¡lidas. Para consultar um ID conhecido:

```powershell
.\.venv\Scripts\python.exe buslinker_v3.py --port COM7 --ids 1
```

O ID de fÃ¡brica do LX-225 Ã© 1, mas pode ter sido alterado. Se nenhum servo responder, siga o [diagnÃ³stico](solucao-de-problemas.md) antes de mover.

## 6. Teste movimento e monitoramento

Depois de conferir o percurso mecÃ¢nico, e supondo ID 1:

```powershell
.\.venv\Scripts\python.exe buslinker_v3.py --port COM7 --ids 1 --move --delta 5 --seconds 2
```

O deslocamento Ã© relativo Ã  posiÃ§Ã£o atual. O alvo precisa respeitar limites internos e mecÃ¢nicos. NÃ£o hÃ¡ retorno automÃ¡tico. A tentativa de parada por software depende da comunicaÃ§Ã£o; fechar a serial nÃ£o desliga torque.

Para grÃ¡ficos sem movimento:

```powershell
.\.venv\Scripts\python.exe buslinker_v3.py monitor --port COM7 --ids 1 --duration 30 --live
```

## 7. Monte o barramento com mais servos

Configure IDs exclusivos **um servo por vez**, usando [change-id](uso.md). `add-id` sÃ³ cadastra nomes no computador. Desligue a alimentaÃ§Ã£o, interligue os servos, dimensione a alimentaÃ§Ã£o do conjunto e consulte todos antes de testar movimento mÃºltiplo.

## Linux e macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m serial.tools.list_ports -v
```

Use a porta encontrada, como `/dev/ttyUSB0` ou `/dev/cu.usbserial-...`. No Ubuntu/Debian, instale `python3-venv` se o sistema indicar ausÃªncia. Para permissÃ£o serial, consulte `ls -l /dev/ttyUSB0`; se o grupo for `dialout`, use `sudo usermod -aG dialout "$USER"` e faÃ§a logout/login. Evite executar a bancada como root.

O [fabricante WCH](https://www.wch-ic.com/downloads/CH341SER.EXE.html?type=en) tambÃ©m disponibiliza pacotes Linux/macOS. Confira primeiro se o sistema jÃ¡ reconhece o conversor. Essas plataformas nÃ£o foram verificadas em hardware neste trabalho.
