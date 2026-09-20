# ESP Tool — joystick de 8 pinos e OLED no ESP32-S3

[Voltar ao README](../README.md)

Guia de montagem do painel apresentado na imagem de referência: ESP32-S3,
display OLED SSD1306 I²C e joystick com os contatos
`RST | SET | MID | RHT | LFT | DWN | UP | COM`.

Esta é uma **pinagem proposta, ainda sem validação no hardware deste projeto**.
O [firmware de diagnóstico](../firmware/joystick_diagnostic/src/main.cpp) permite
testar os contatos e o OLED. Ele não controla os LX-225: essa integração ainda
precisa ser implementada.

## Gravar pelo VS Code com PlatformIO

1. No VS Code, abra **Extensões** (`Ctrl+Shift+X`) e confira se **PlatformIO IDE**
   está instalado. Aguarde a inicialização da extensão.
2. Use **Arquivo → Abrir Pasta** e selecione `firmware/joystick_diagnostic`
   dentro deste repositório. Essa é a pasta que contém `platformio.ini`.
3. Confirme o modelo da placa antes de gravar. O perfil de referência é
   **ESP32-S3-DevKitC-1 N8 (8 MB de flash)**, sem uso de PSRAM. Outra revisão
   pode exigir ajustes no `platformio.ini`.
4. Conecte um cabo USB de dados. Abra o ícone do PlatformIO na lateral e,
   em **Project Tasks**, escolha o ambiente conforme o conector utilizado:

   | Conector da placa | Ambiente |
   | --- | --- |
   | UART / COM (conversor USB–serial) | `uart` |
   | USB / OTG (USB nativa do ESP32-S3) | `usb` |

5. Nesse ambiente, execute **General → Build**. A primeira compilação baixa
   a plataforma e as bibliotecas automaticamente.
6. Execute **General → Upload** para gravar na placa. Se houver vários
   dispositivos seriais, identifique a porta pelo Gerenciador de Dispositivos
   do Windows e acrescente `upload_port = COM7` e `monitor_port = COM7` à seção
   do ambiente escolhido, substituindo COM7 pela porta real. A USB nativa pode
   mudar de porta após a gravação; confira novamente se necessário.
7. Abra **General → Monitor**, a **115200 baud**. Feche outros monitores
   seriais que estejam usando a mesma porta.

Se a gravação ficar em `Connecting...`, segure **BOOT da placa**, aperte e solte
**RESET/EN da placa** e solte BOOT; tente Upload novamente. Depois da gravação,
se não iniciar, pressione RESET/EN. Esses são os botões da placa ESP32-S3,
não SET/RST do joystick.

O OLED deve exibir `ESP TOOL - TESTE`. Na serial, a cada dois segundos aparece:

```text
ESTADO: UP=1 DWN=1 LFT=1 RHT=1 MID=1 SET=1 RST=1 | OLED=inicializado (0x3C) | 0=pressionado, 1=solto
```

Ao acionar UP, por exemplo, aparece `UP GPIO 4: PRESSIONADO (0)`; ao soltar,
`UP GPIO 4: SOLTO (1)`. O OLED também atualiza os estados. Se não for encontrado,
o diagnóstico continua pela serial. `OLED=inicializado` informa a inicialização
do software, não comprova que o display esteja visualmente funcionando.

O padrão é **128 × 64 pixels**. Se o seu SSD1306 for 128 × 32, altere
`-D OLED_HEIGHT=64` para `-D OLED_HEIGHT=32` em `platformio.ini` e grave novamente.
O firmware busca endereços I²C na inicialização, prefere `0x3C` e aceita `0x3D`.
Um dispositivo responder nesse endereço não confirma que seja SSD1306.
Após corrigir fios com a alimentação desligada, religue para repetir a busca.

Alternativa pelo terminal do PlatformIO, dentro da pasta do firmware:

```powershell
pio run -e uart
pio run -e uart -t upload
pio device monitor -b 115200
```

Para USB nativa, substitua `-e uart` por `-e usb` nos dois primeiros comandos.
Se houver várias portas, informe `--upload-port COM7` no comando de Upload e
`--port COM7` no monitor, usando a porta real.

Referências de configuração: [perfil ESP32-S3-DevKitC-1 do PlatformIO](https://docs.platformio.org/en/latest/boards/espressif32/esp32-s3-devkitc-1.html)
e [biblioteca Adafruit SSD1306](https://github.com/adafruit/Adafruit_SSD1306).

## Componentes

- Placa de desenvolvimento ESP32-S3 com os GPIOs da tabela acessíveis.
- OLED SSD1306 com interface I²C, compatível com alimentação de 3,3 V.
- Joystick digital de 8 pinos, conforme os nomes acima.
- Fios de conexão e cabo USB de dados para o ESP32-S3.
- Multímetro para conferir continuidade e identificação dos contatos.

Esse joystick tem contatos direcionais e botões, em vez de saídas analógicas
X/Y. `MID` é o clique central; `SET` e `RST` são botões adicionais. Os nomes
não definem ações no programa: menus, confirmação e retorno dependem do firmware.

## Pinagem de referência

Use os **nomes impressos nos módulos e os números de GPIO**, não a posição
visual dos conectores. GPIO 4 significa o pino marcado `4`/`IO4` na placa,
não o quarto pino do conector. Confira o pinout da revisão exata do seu ESP32-S3
e se esses GPIOs estão disponíveis antes de montar.

### Joystick

| Pino do módulo | Função | ESP32-S3 | Configuração prevista |
| --- | --- | --- | --- |
| COM | Contato comum | GND | Terra comum |
| UP | Cima | GPIO 4 | `INPUT_PULLUP` |
| DWN | Baixo | GPIO 5 | `INPUT_PULLUP` |
| LFT | Esquerda | GPIO 6 | `INPUT_PULLUP` |
| RHT | Direita | GPIO 7 | `INPUT_PULLUP` |
| MID | Clique central / OK | GPIO 15 | `INPUT_PULLUP` |
| SET | Botão adicional | GPIO 16 | `INPUT_PULLUP` |
| RST | Botão adicional | GPIO 17 | `INPUT_PULLUP` |

Para o módulo de contatos mostrado, COM vai ao GND; não existe conexão VCC
nessa lista de oito pinos. Não aplique alimentação a um contato para tentar
alimentar o joystick. **RST não vai ao EN/RST da placa**, e SET não vai ao BOOT.

### OLED SSD1306

| Pino do OLED | ESP32-S3 |
| --- | --- |
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 8 |
| SCL | GPIO 9 |

O endereço I²C indicado na referência é **`0x3C`**. Confirme por varredura I²C
antes de configurar a biblioteca. Confira também a resolução do seu display;
o nome SSD1306, sozinho, não informa a resolução do módulo.

### Atenção às divergências da imagem

As tabelas da imagem fornecida são a referência para este guia. O desenho dos
fios não deve ser usado como mapa elétrico: no OLED, por exemplo, o fio vermelho
chega ao contato rotulado GND, embora a tabela indique corretamente VCC → 3V3.
A ordem dos contatos desenhados no joystick também difere entre as duas vistas.

Antes de ligar, confira cada conexão pela serigrafia do módulo real. A sequência
`RST | SET | MID | RHT | LFT | DWN | UP | COM` identifica a vista de referência;
olhar pelo lado oposto pode inverter a ordem aparente.

## Montagem passo a passo

1. Desconecte o USB e qualquer outra alimentação.
2. Identifique GND, 3V3 e todos os GPIOs na sua placa.
3. Com o joystick desconectado, meça continuidade entre COM e cada contato.
   Ao acionar a direção ou botão correspondente, o contato deve fechar.
   Se o resultado divergir, interrompa a montagem e confirme o modelo do módulo.
4. Ligue COM ao GND e os sete contatos aos GPIOs da tabela.
5. Ligue o OLED: GND ao GND, VCC ao 3V3, SDA ao GPIO 8 e SCL ao GPIO 9.
6. Confira a polaridade do OLED e se não há curto entre 3V3 e GND.
7. Conecte o USB e faça primeiro a verificação das entradas e do display.

Use **3,3 V no circuito do painel**; não conecte 5 V aos GPIOs. O joystick e
o OLED devem compartilhar o GND do ESP32-S3. A alimentação dos servos LX-225
descrita no README principal é separada: não a conecte ao 3V3 nem aos GPIOs.

## Comportamento do firmware

O firmware configura as sete entradas como `INPUT_PULLUP` e usa SDA = 8 e
SCL = 9 na inicialização do I²C, com `Wire.begin(8, 9)`.

| Estado do contato | Leitura esperada |
| --- | --- |
| Solto / aberto | `HIGH` (1) |
| Pressionado / fechado com COM | `LOW` (0) |

O firmware aceita mudanças após **25 ms de estabilidade** (*debounce*) e
informa tanto o pressionamento quanto a soltura. Segurar um botão não gera
novos eventos de pressionamento. O resumo periódico continua aparecendo a cada
dois segundos, mesmo sem eventos, para permitir abrir o monitor após o boot.

## Verificação inicial

Depois de gravar o firmware e abrir o monitor serial:

1. Confira se todas as entradas ficam em `HIGH` sem acionamento.
2. Acione UP, DWN, LFT e RHT individualmente e confira o GPIO correspondente.
3. Pressione MID, SET e RST; cada um deve alterar somente sua entrada.
4. Solte cada contato e confirme o retorno a `HIGH`.
5. Confira o endereço do OLED informado pelo firmware (busca automática no boot).
6. Confira o texto e os estados exibidos no OLED.

O botão RST do joystick não deve reiniciar a placa. Valide o painel antes de
implementar comandos de movimento para os servos.

## Solução de problemas

| Sintoma | O que conferir |
| --- | --- |
| Nenhum contato responde | COM ligado ao GND, continuidade dos fios e configuração `INPUT_PULLUP`. |
| Entrada sempre pressionada | Curto ao GND, contato preso ou identificação incorreta do pino. |
| Leituras variam sem tocar | GND comum, conexões firmes e pull-up habilitado. |
| Direções ou botões trocados | Serigrafia do módulo, orientação do conector e tabela de GPIOs. |
| Um toque gera vários eventos | Debounce e detecção da transição no firmware. |
| RST reinicia o ESP32-S3 | Ligação indevida ao EN/RST ou curto durante o acionamento. |
| OLED não aparece na varredura | Alimentação, GND, SDA/SCL e configuração explícita dos pinos I²C. |
| OLED aparece, mas fica apagado | Endereço usado pela biblioteca, resolução e sequência de inicialização. |

## Relação com a bancada de servos

Os scripts `buslinker_v2_5.py` e `buslinker_v3.py` continuam sendo executados
no computador e se comunicam com os servos pela BusLinker. Eles não leem este
joystick e não recebem comandos do ESP32-S3.

Uma futura integração precisa ampliar o firmware, definir o transporte de comandos
até o computador, as funções dos botões e o tratamento de perda de comunicação.
A documentação da bancada permanece no [README](../README.md) e no
[guia Gaia/LX-225](gaia_lx225.md).
