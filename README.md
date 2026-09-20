# Gaia â€” servos LX-225, BusLinker e peÃ§as mecÃ¢nicas

Ferramentas de bancada dos atuadores do humanoide **Gaia**: controle Python de servos Hiwonder LX-225 com BusLinker V2.5 ou V3.0, leitura de sensores, grÃ¡ficos, configuraÃ§Ã£o de IDs, calibraÃ§Ã£o e arquivos mecÃ¢nicos.

**Comece com um Ãºnico servo:** confirme a comunicaÃ§Ã£o, teste um movimento pequeno e sÃ³ depois monte o barramento com vÃ¡rios IDs.

## Encontre o que vocÃª precisa

| Queroâ€¦ | Abrir |
| --- | --- |
| Instalar do zero e identificar a porta USB | [Tutorial de instalaÃ§Ã£o](docs/instalacao.md) |
| Baixar datasheets, manuais e esquemas | [DocumentaÃ§Ã£o tÃ©cnica V2.5, V3 e LX-225](docs/datasheets/README.md) |
| Instalar software Hiwonder ou driver USB | [Softwares e drivers](docs/softwares-e-drivers.md) |
| Ler sensores, mover, gerar grÃ¡ficos ou calibrar | [Manual dos comandos Python](docs/uso.md) |
| Resolver erros de comunicaÃ§Ã£o ou movimento | [SoluÃ§Ã£o de problemas](docs/solucao-de-problemas.md) |
| Baixar CAD LX-224/LX-225 e suportes | [CatÃ¡logo mecÃ¢nico](hardware/README.md) |
| Integrar os atuadores no humanoide | [Arquitetura Gaia](docs/gaia_lx225.md) |
| Montar joystick e display ESP32-S3 | [Guia do joystick](docs/joystick.md) |

## Como funciona

```mermaid
flowchart LR
    PC[Computador com Python] -->|USB de dados| B[BusLinker V2.5 ou V3.0]
    F[Fonte externa para LX-225] -->|AlimentaÃ§Ã£o| B
    B <-->|Barramento TTL| S1[Servo ID 1]
    S1 <-->|Mesmo barramento| S2[Servo ID 2]
```

A **BusLinker** conecta o computador ao barramento. O **driver USB** faz aparecer a porta COM no sistema. Os **scripts Python** enviam comandos pela porta; cada servo tem um ID. O LX-225 recebe comandos seriais, nÃ£o pulsos de um controlador de servo PWM convencional.

**Alimente o LX-225 com 6â€“8,4 V.** A corrente de travamento informada Ã© 4 A por servo: considere picos simultÃ¢neos, cabos e conectores ao dimensionar a alimentaÃ§Ã£o. A tensÃ£o mÃ¡xima aceita pela placa nÃ£o Ã© a tensÃ£o mÃ¡xima do servo. [EspecificaÃ§Ãµes Hiwonder](https://www.hiwonder.com/products/lx-225).

## Primeiro teste no Windows

VocÃª precisa de uma BusLinker, um LX-225, cabo de servo, cabo USB **de dados**, fonte apropriada e Python. O [tutorial completo](docs/instalacao.md) explica as conexÃµes e a instalaÃ§Ã£o.

1. Baixe o repositÃ³rio em **Code â†’ Download ZIP** e extraia tudo, ou clone pelo endereÃ§o mostrado em **Code**. Abra um terminal na pasta deste README.
2. Crie o ambiente e instale as dependÃªncias:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Com a alimentaÃ§Ã£o desligada, conecte um servo e confira polaridade, conector e seleÃ§Ã£o USB da sua revisÃ£o. Ligue a fonte e conecte o USB. Feche os outros programas que usam a serial e identifique a porta:

   ```powershell
   .\.venv\Scripts\python.exe -m serial.tools.list_ports -v
   ```

4. Substitua `COM7` pela porta identificada e execute **apenas o comando da sua placa**:

   ```powershell
   # BusLinker V2.5 â€” somente leitura
   .\.venv\Scripts\python.exe buslinker_v2_5.py --port COM7 --scan
   # BusLinker V3.0 â€” somente leitura
   .\.venv\Scripts\python.exe buslinker_v3.py --port COM7 --scan
   ```

A busca percorre IDs de 0 a 253 e mostra os que responderam, com posiÃ§Ã£o, tensÃ£o e temperatura. Se nada responder, siga o [diagnÃ³stico](docs/solucao-de-problemas.md). IDs duplicados nÃ£o permitem contar separadamente os servos fÃ­sicos.

5. Confira o percurso mecÃ¢nico antes de mover. Exemplo para **ID 1 e V3**:

   ```powershell
   .\.venv\Scripts\python.exe buslinker_v3.py --port COM7 --ids 1 --move --delta 5 --seconds 2
   ```

Isso solicita **+5Â° a partir da posiÃ§Ã£o atual**, em 2 segundos, sem retorno automÃ¡tico. O teste verifica modo de posiÃ§Ã£o, limites e tensÃ£o; pode habilitar torque. `Ctrl+C` tenta parar o servo, mas uma falha de comunicaÃ§Ã£o pode impedir a parada. Fechar o programa nÃ£o desliga o torque.

## Qual arquivo executar?

| Placa | Arquivo autÃ´nomo | Classe para importar |
| --- | --- | --- |
| BusLinker V2.5 | [buslinker_v2_5.py](buslinker_v2_5.py) | `BusLinkerV2_5` |
| BusLinker V3.0 | [buslinker_v3.py](buslinker_v3.py) | `BusLinkerV3` |

Cada arquivo inclui comunicaÃ§Ã£o, menu, grÃ¡ficos, IDs e calibraÃ§Ã£o. Pode ser copiado sozinho, desde que `pyserial` e `matplotlib` estejam instalados. Os dois usam o protocolo LX-225 a **115200 baud**. O nome V3 nÃ£o ativa protocolos de outros modelos de servo.

Com o ambiente virtual ativo, exemplos para V3:

```powershell
# Menu de consulta e movimento solicitado pelo usuÃ¡rio
python buslinker_v3.py --interactive --port COM7 --ids 1
# GrÃ¡ficos e CSV, sem movimentar
python buslinker_v3.py monitor --port COM7 --ids 1 --duration 30 --live
# Nome local da junta; nÃ£o muda o ID fÃ­sico
python buslinker_v3.py add-id --id 1 --name joelho_esquerdo
```

O monitor salva dados em `resultados/`; os nomes ficam em `servos.json`. Ambos sÃ£o locais e ignorados pelo Git. Veja [uso avanÃ§ado](docs/uso.md) para troca de ID fÃ­sico, calibraÃ§Ã£o, offset e sincronizaÃ§Ã£o.

## CAD e suportes

O [catÃ¡logo mecÃ¢nico](hardware/README.md) reÃºne o CAD compartilhado LX-224/LX-225 informado pelo mantenedor, a montagem SolidWorks e os suportes em Inventor, STEP e STL.

- **Montagem do servo:** [CAD LX-224/LX-225](hardware/cad/servo-lx224-lx225/).
- **Imprimir suportes:** [STL](hardware/suportes/gaia-3d/STL/).
- **Adaptar em CAD:** [STEP](hardware/suportes/gaia-3d/STEP/).
- **PeÃ§as nativas:** [Inventor Gaia 3D](hardware/suportes/gaia-3d/IPT/) e [peÃ§as LX-225](hardware/suportes/pecas-lx225/).

Confira unidades, furos, folgas e percurso antes de fabricar. A equivalÃªncia do CAD Ã© uma referÃªncia mecÃ¢nica do projeto; as especificaÃ§Ãµes elÃ©tricas utilizadas sÃ£o as do LX-225.

## OrganizaÃ§Ã£o

```text
â”œâ”€â”€ README.md                    # Comece aqui
â”œâ”€â”€ requirements.txt             # DependÃªncias Python
â”œâ”€â”€ buslinker_v2_5.py             # Programa completo para V2.5
â”œâ”€â”€ buslinker_v3.py               # Programa completo para V3.0
â”œâ”€â”€ servo_testbench.py            # Fonte do driver compartilhado
â”œâ”€â”€ bench_tools.py               # Monitoramento, cadastro e calibraÃ§Ã£o
â”œâ”€â”€ test_servos.py                # Interface de bancada
â”œâ”€â”€ docs/                        # InstalaÃ§Ã£o, uso e problemas
â”‚   â””â”€â”€ datasheets/               # Manuais, esquemas e fontes oficiais
â”œâ”€â”€ hardware/                    # CAD e suportes, com catÃ¡logo
â”œâ”€â”€ firmware/joystick_diagnostic/ # DiagnÃ³stico do joystick/OLED
â”œâ”€â”€ tests/                       # Testes com serial simulada
â””â”€â”€ tools/                       # DiagnÃ³stico e geraÃ§Ã£o dos programas
```

## Desenvolvimento e limites

O projeto Ã© uma bancada de atuadores. Marcha, equilÃ­brio e seguranÃ§a do humanoide completo dependem da integraÃ§Ã£o. A velocidade exibida Ã© calculada entre leituras de posiÃ§Ã£o; corrente e torque nÃ£o sÃ£o medidos pelo driver. O firmware do joystick testa botÃµes e OLED e ainda nÃ£o comanda servos.

Para validar sem hardware:

```powershell
python -m unittest discover -s tests -v
```

Os testes simulados verificam software e protocolo, sem certificar o funcionamento elÃ©trico/mecÃ¢nico. Para mudar os programas autÃ´nomos, edite `servo_testbench.py`, `bench_tools.py` e `test_servos.py`, depois execute `python tools/build_standalone.py`.

Ao relatar um problema, inclua revisÃ£o da placa, modelo e IDs dos servos, sistema operacional, comando, mensagem completa e alimentaÃ§Ã£o usada.
