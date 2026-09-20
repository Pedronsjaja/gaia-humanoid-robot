# Manual de uso dos scripts Python

[Voltar ao README](../README.md) · [Instalação](instalacao.md) · [Solução de problemas](solucao-de-problemas.md)

Execute os comandos na raiz do repositório, com o ambiente virtual ativo.

## Teste de bancada

### Descobrir porta, IDs e quantidade

Execute sem argumentos (tambem funciona pelo botao Executar do editor):

```powershell
python buslinker_v3.py
```

Se houver uma unica porta serial USB, ela sera selecionada automaticamente.
O programa consulta os IDs de 0 a 253, em cerca de 12 segundos, e mostra os IDs
encontrados, a quantidade e uma tabela de posicao, tensao e temperatura.
A busca apenas consulta os servos. IDs duplicados nao permitem contar
separadamente os servos fisicos, e servos sem resposta nao entram na contagem.
Nenhum cadastro ou ID fisico e alterado.

Se houver mais de uma porta USB, escolha a porta explicitamente:

```powershell
python buslinker_v3.py --port COM7 --scan
# Consultar diretamente os IDs conhecidos, sem esperar a busca:
python buslinker_v3.py --port COM7 --ids 5 6
```

O mesmo funciona com `buslinker_v2_5.py`. Para movimentar, `--move` continua
exigindo `--ids` explicitos e nao pode ser combinado com `--scan`.

### Menu para mover pelo terminal do VS Code

Ao executar sem argumentos em um terminal, o programa abre um menu depois da
busca: **1** consulta as leituras, **2** move um servo, **3** busca os IDs novamente,
**4** move varios servos juntos, com inicio em sequencia rapida, e **0** sai. Se a busca nao encontrar
servos, o menu permite tentar novamente.
Para abrir o menu explicitamente e consultar direto o ID conhecido:

```powershell
python buslinker_v3.py --interactive --port COM7 --ids 6
```

Na opcao **2**, escolha o ID, o deslocamento em graus e o tempo em segundos.
Enter seleciona o unico ID encontrado, deslocamento de +5 graus e tempo de
2 segundos. Valores negativos movem no sentido contrario. O deslocamento
permitido e de -100 a +100 graus, relativo a uma leitura nova da posicao atual,
e o tempo pode variar de 0.5 a 30 segundos. O alvo deve estar entre 0 e 240 graus.
Deixe o eixo livre antes de selecionar o movimento. Nao ha retorno automatico.
Ctrl+C interrompe o programa e, durante um movimento, tenta parar o servo.
O menu nao altera IDs nem offsets. `--scan` continua sendo uma consulta sem menu.

Antes do movimento, o teste confere modo de posicao e limites internos do servo.
Sem `--synchronized`, envia o comando direto de movimento e consulta o alvo e
tempo recebidos. Se o torque estiver desligado, habilita-o somente depois de
confirmar esse alvo. Falhas interrompem o teste com tentativa de parada.
Habilitar torque ocorre apenas ao pedir movimento, nunca na busca ou leitura.
Durante o movimento, cada leitura de tensao tambem e conferida. Se qualquer
servo informar tensao fora de 6 a 8.4 V, o teste interrompe e tenta parar todos
os selecionados. A mensagem mostra o ID e a tensao observada. Confira a
alimentacao antes de repetir: aumentar o deslocamento nao corrige queda de
tensao. A parada nao desliga o torque, e perda de comunicacao pode impedi-la.
Com `--synchronized`, habilita torque na posicao atual quando necessario,
confirma todos os alvos preparados e envia um unico inicio por broadcast.

Na opcao **4**, digite os IDs separados por espaco, por exemplo `5 6` (Enter usa
todos os encontrados), o deslocamento comum e o tempo comum. Cada servo parte
da propria posicao atual. Todos devem responder e ter seus limites conferidos
antes de qualquer movimento. O torque e habilitado na posicao atual se necessario.
Os comandos diretos sao enviados a todos antes das consultas de confirmacao,
com pequena diferenca entre os instantes de inicio. A opcao nao depende dos
comandos de preparo/sincronizacao e nao envia broadcast. O mesmo teste pelo terminal:

```powershell
python buslinker_v3.py --port COM7 --ids 5 6 --move --delta -20 --seconds 3
```

Para sincronizacao por broadcast, existe a opcao avancada `--synchronized`, que
depende da confirmacao de alvos preparados por todos os servos. Ela nao e usada
pela opcao 4 do menu. Nesse modo, use barramento dedicado: o broadcast inicia todos os
alvos pendentes, inclusive de outros IDs. Se algum servo nao confirmar o alvo
preparado, o inicio nao e enviado e o teste tenta parar todos os selecionados.
Reinicie a alimentacao apos falha de preparo antes de outro teste sincronizado,
pois a parada nao garante que alvos pendentes tenham sido apagados.

O mesmo limite de deslocamento vale para `--move --delta`. Por exemplo,
`--move --delta 100 --seconds 5` avanca 100 graus em 5 segundos, desde que o
alvo nao ultrapasse 240 graus. A partir de 151.68 graus, +100 seria rejeitado;
-100 teria alvo de 51.68 graus. Confira o percurso mecanico antes de executar.

### Monitoramento e gráficos

Instale também a dependência de gráficos: `python -m pip install -r requirements.txt`.
Todos os comandos abaixo funcionam nas duas placas: para V3, substitua
`buslinker_v2_5.py` por `buslinker_v3.py`.

```powershell
python buslinker_v2_5.py monitor --port COM7 --ids 1 2 --duration 30 --live
```

Mostra posição (graus), velocidade estimada (graus/s), tensão (V) e temperatura
(°C). `--live` abre quatro gráficos durante a coleta; sem ele, os gráficos são
gerados ao final. Cada execução cria uma subpasta com data/hora em `resultados/`,
contendo `telemetria.csv` e `graficos.png`. Use `--output outra_pasta` para mudar
o destino. Ctrl+C preserva os dados já coletados. Falhas de leitura aparecem no
CSV e como lacunas nos gráficos, sem inventar valores. O código de saída é 1
se houve falha de leitura. O monitor apenas lê, não movimenta nem para servos.

`--interval 0.1` define a pausa entre rodadas; a taxa real inclui o tempo das
leituras e dos gráficos. Os sensores são lidos sequencialmente. O tempo registrado
é o da leitura de posição. A primeira velocidade é NaN, por faltar amostra anterior.

### Cadastrar IDs manualmente e editar nomes

```powershell
python buslinker_v2_5.py add-id --id 1 --name quadril
python buslinker_v2_5.py add-id --id 2 --name joelho
python buslinker_v2_5.py list-ids
```

O cadastro fica em `servos.json`, compartilhado entre as versões. Repetir `add-id`
com o mesmo ID atualiza o nome. Isso não muda o ID físico nem exige placa conectada.
Use `--registry outro.json` para outro cadastro. Em `monitor` e `calibrate`, omitir
`--ids` seleciona todos os IDs cadastrados.

### Alterar o ID físico

Conecte **somente o servo a reconfigurar**. IDs duplicados não podem ser
identificados de forma confiável pelo barramento; `--single-servo` declara essa
condição física, não a detecta automaticamente.

```powershell
python buslinker_v2_5.py change-id --port COM7 --from-id 1 --to-id 3 --single-servo
```

Confere o ID atual, rejeita destino que já responde ou consta no cadastro, envia
a alteração, verifica o novo ID e atualiza o JSON. Se a confirmação falhar, o ID
pode já ter mudado: consulte os IDs antigo e novo antes de repetir. Uma falha ao
salvar o cadastro depois da confirmação não desfaz o ID físico.

### Teste de calibração / acompanhamento de posição

```powershell
python buslinker_v2_5.py calibrate --port COM7 --ids 1 2 --deltas -5 0 5 0 --seconds 2 --samples 5 --tolerance 2 --live
```

O teste movimenta os servos em deslocamentos relativos à posição inicial,
limitados a ±10°. Confira espaço livre e limites mecânicos antes de executar.
Após cada movimento, aguarda `--settle 0.5` segundos e mede cinco vezes.
`calibracao.csv` registra alvo efetivamente enviado (quantizado em 0,24°), média
medida, erro (medido − alvo), dispersão e aprovação pela tolerância em graus.
O código de saída 2 indica erro acima da tolerância; 1 indica falha de execução.
Os quatro gráficos e o CSV de telemetria também são gerados durante esse teste.

O padrão percorre -5°, 0°, +5°, 0° em relação à posição inicial. Uma lista
personalizada termina no último alvo. Em falha ou Ctrl+C, tenta parar todos os
IDs e preserva os resultados parciais, sem tentar retornar automaticamente.
O teste interrompe se a tensão sair de 6–8,4 V ou se a temperatura chegar a
`--max-temp 60` °C (limiar do programa, não configuração permanente do servo).

Esse ensaio usa o sensor interno: mede acompanhamento/repetibilidade, mas **não
mede o erro absoluto do zero mecânico**. Para isso, use referência externa
(goniômetro, alinhamento mecânico ou encoder independente).

### Consultar, experimentar e gravar correção de zero

```powershell
# Consultar o offset atual
python buslinker_v2_5.py offset --port COM7 --id 1
# Exemplo: definir offset absoluto de 5 ticks = 1.20 grau, temporariamente
python buslinker_v2_5.py offset --port COM7 --id 1 --ticks 5
# Depois de conferir fisicamente o resultado, gravar o mesmo valor
python buslinker_v2_5.py offset --port COM7 --id 1 --ticks 5 --save
```

Use o valor obtido na sua medição, não necessariamente 5. O offset aceito é um
inteiro de -125 a +125 ticks, cada tick equivalente a 0,24°. É um valor absoluto,
não um incremento sobre o anterior. O comando pode movimentar o eixo. Anote o
offset anterior mostrado no terminal para restaurá-lo se necessário. Experimente
temporariamente e confira direção/magnitude com a referência externa antes de salvar.

`--save` envia o comando de gravação somente após confirmar o offset temporário
por leitura. A leitura após salvar verifica o valor ativo; a persistência deve ser
conferida desligando e religando a alimentação e consultando novamente. O programa
nunca calcula nem grava automaticamente um offset a partir do erro do sensor interno.

### Movimento básico

Substitua COM7 pela porta da sua placa. Primeiro, teste somente as leituras:

```powershell
# BusLinker V2.5
python buslinker_v2_5.py --port COM7 --ids 1 2
# BusLinker V3
python buslinker_v3.py --port COM7 --ids 1 2
```

Depois, com os servos livres e o percurso conferido, teste um deslocamento de
5 graus em 2 segundos a partir da posição atual:

```powershell
python buslinker_v2_5.py --port COM7 --ids 1 2 --move --delta 5 --seconds 2
```

Para V3.0, use `buslinker_v3.py` no mesmo comando.

Para três ou mais, acrescente os IDs em `--ids 1 2 3`. O programa verifica todos
antes de movimentar, acompanha posição/tensão e tenta parar cada servo ao
concluir, ocorrer falha ou receber Ctrl+C. Não retorna à posição inicial.
Uma falha de comunicação pode impedir a parada; fechar a serial não desliga o torque.

`--synchronized` usa início por broadcast: afeta **todos os movimentos pendentes
no barramento**, inclusive de IDs não listados. Use apenas em barramento dedicado
ao teste, sem movimentos antigos pendentes. Por padrão, o início é individual.
Uma falha durante a preparação pode deixar comandos pendentes nos servos; não
envie broadcast depois disso sem restabelecer um estado conhecido.

Configure IDs individualmente antes de interligar servos com o ID padrão 1.
Use alimentação externa de 6–8,4 V, dimensionada para a carga: a especificação
informa 4 A por servo travado (8 A para dois nessa condição). Confira polaridade,
terra comum e o modo USB/servo da revisão da sua BusLinker. Não use a tensão de
servos de alta tensão para alimentar o LX-225.

Referências: [LX-225](https://www.hiwonder.com/products/lx-225) e
[protocolo Hiwonder](https://engineering.purdue.edu/477grp4/Team/journal/img%20-%20Juho/week7/servo%20bus%20protocol.pdf).

## Validação sem hardware

```powershell
python -m unittest discover -s tests -v
```

Os testes usam serial simulada: pacotes, eco, respostas fragmentadas/corrompidas,
entradas inválidas, velocidade e partida de três servos. Não comprovam o
funcionamento elétrico/mecânico da placa ou dos servos.

## Limites do driver

- Ângulos fora de 0–240 graus, NaN e infinito são rejeitados, sem saturação silenciosa.
- Tempos fora de 0–30 segundos são rejeitados. Zero é permitido pelo protocolo;
  o programa de bancada exige ao menos 0,5 segundo.
- A velocidade é aproximada, limitada pela mecânica e pela resolução do protocolo;
  movimentos calculados acima de 30 segundos são rejeitados.
- As leituras retornam assim que recebem pacote válido; 45 ms é o limite de espera
  por comando. Posição, tensão e temperatura são lidas sequencialmente.
- Use uma única sequência de chamadas por barramento; não compartilhe a instância
  entre threads. Não há garantias de controle em tempo real para equilíbrio.
- O teste de movimento exige modo de posição e verifica os limites internos. Ao solicitar movimento, pode habilitar torque após confirmar o alvo; consultas não habilitam torque.

## Exemplo mínimo

```python
from servo_testbench import LX225Bus

with LX225Bus("COM7") as bus:
    bus.move_at_speed(5, angle_deg=90, velocity_dps=60)
    state = bus.read_servo(5, identifier="joelho_direito")
    print(state)
    bus.stop(5)
```

`move_at_speed` converte velocidade em tempo de movimento, pois o protocolo do
servo recebe posição e tempo. A velocidade retornada por `read_servo` é calculada
entre duas leituras consecutivas.
Na primeira leitura, a velocidade é `NaN` porque ainda não há amostra anterior.

Para nomes estáveis do robô, preencha `SERVO_IDENTIFIERS` no módulo. O nome não
altera o ID físico e permite trocar a identificação mecânica sem reescrever o
código de controle.

## Manutencao dos arquivos completos

`servo_testbench.py`, `bench_tools.py` e `test_servos.py` permanecem como fontes
de desenvolvimento. Depois de altera-los, execute `python tools/build_standalone.py`
para atualizar os dois arquivos completos de forma identica. Alteracoes manuais
nos arquivos gerados serao substituidas na proxima geracao. Para nomes dos servos,
prefira o comando `add-id`, que salva em `servos.json` fora do codigo.
