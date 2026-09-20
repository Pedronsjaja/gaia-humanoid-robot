# Gaia: integracao dos servos LX-225

Este documento define o limite do modulo de atuadores do robo humanoide Gaia.
Ele concentra a comunicacao de baixo nivel com os servos Hiwonder LX-225 e
mantem a camada de controle do robo independente da placa usada no barramento.

## Arquitetura

```text
Gaia (controle de marcha, cinemática e segurança)
              |
              v
  modulo de atuadores LX-225
              |
       BusLinker V2.5 ou V3
              |
       barramento serial TTL
              |
       servos LX-225 por ID
```

Os drivers deste repositorio nao definem a cinemática do Gaia. Eles apenas
fazem transporte de comandos, leitura de estado e verificacoes basicas do
atuador. A associacao entre ID e junta deve ficar no cadastro do projeto Gaia.

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `buslinker_v2_5.py` | Driver e ferramentas para BusLinker V2.5 |
| `buslinker_v3.py` | Driver e ferramentas para BusLinker V3 |
| `servo_testbench.py` | Implementacao base reutilizavel |
| `tests/` | Testes sem hardware conectado |
| `tools/` | Geracao e manutencao dos drivers autonomos |

Os arquivos V2.5 e V3 sao autonomos para facilitar a copia para o computador do
Gaia. Use somente um deles no programa final, conforme a placa instalada.

## Cadastro de juntas

O ID fisico nao deve ser usado como nome da junta. O Gaia deve manter um mapa
semantico, por exemplo:

```json
{
  "1": "quadril_esquerdo_pitch",
  "2": "quadril_direito_pitch",
  "3": "joelho_esquerdo_pitch",
  "4": "joelho_direito_pitch"
}
```

Esse cadastro identifica o atuador, mas nao substitui a calibracao de sentido,
zero mecanico, limites e reducao da junta. O arquivo `servos.json` pode ser
usado para os nomes simples do driver; o mapa completo do Gaia deve permanecer
na configuracao do robo.

## Parametros mantidos

- `servo_id`: endereco de 0 a 253 no barramento.
- `identifier`: nome estavel da junta ou atuador.
- `angle_deg`: posicao em graus; o LX-225 usa 0 a 240 graus no protocolo.
- `velocity_dps`: velocidade estimada pela diferenca entre leituras.
- `voltage_v`: tensao informada pelo servo.
- `temperature_c`: temperatura interna, usada para protecao no monitoramento.

A velocidade do comando e convertida para tempo de movimento, porque o pacote
do LX-225 recebe alvo angular e duracao, nao uma velocidade independente.

## Uso com o BusLinker V3

```powershell
python buslinker_v3.py monitor --port COM7 --ids 1 2 --duration 30
```

Para testar um movimento curto, primeiro confirme que os servos estao livres e
que os IDs estao corretos:

```powershell
python buslinker_v3.py --port COM7 --ids 1 2 --move --delta 5 --seconds 2
```

No codigo Python:

```python
from buslinker_v3 import LX225Bus

with LX225Bus("COM7") as bus:
    bus.move_many([
        (1, 90.0, 1.0),
        (2, 90.0, 1.0),
    ])
    estado = bus.read_servo(1, "quadril_esquerdo_pitch")
    print(estado.angle_deg, estado.velocity_dps, estado.voltage_v)
    bus.stop(1)
    bus.stop(2)
```

## Sequencia recomendada para integrar no Gaia

1. Conectar um unico servo e confirmar o ID.
2. Cadastrar o nome da junta sem alterar o ID fisico.
3. Testar leitura de angulo, tensao e temperatura.
4. Testar deslocamento pequeno, com limites mecanicos livres.
5. Calibrar zero, sentido e limites da junta.
6. Repetir para cada atuador.
7. Somente depois conectar o barramento completo e testar movimentos coordenados.

## Limites e seguranca

- Alimentar o LX-225 com 6 a 8,4 V.
- Usar fonte dimensionada para a corrente de varios servos travados.
- Garantir terra comum entre fonte, BusLinker e servos.
- Cada servo deve possuir ID unico.
- Alteracao de ID deve ser feita com apenas um servo conectado.
- Nao usar broadcast em um barramento compartilhado sem saber quais comandos
  pendentes existem.
- O monitoramento nao substitui um limite mecanico ou uma parada de emergencia
  eletrica.
- Corrente e torque individual nao sao fornecidos pelo protocolo padrao do
  LX-225; a avaliacao de carga exige sensor externo e calibracao.

## O que falta para o modelo completo do Gaia

Este modulo ainda nao define:

- quantidade e nomes finais das juntas;
- limites angulares de cada junta;
- sentido positivo de cada motor;
- offsets mecanicos;
- dimensoes dos suportes e furos;
- sequencias de marcha;
- parada de emergencia do sistema inteiro.

Esses dados devem entrar em uma configuracao propria do Gaia, sem alterar o
protocolo de comunicacao dos drivers.

## Guias complementares da equipe

[Programação](https://github.com/Pedronsjaja/gaia-humanoid-simulation/blob/main/docs/programacao/README.md) · [Simulação OP3](https://github.com/Pedronsjaja/gaia-humanoid-simulation/blob/main/docs/simulacao/README.md) · [Modelo Gaia](https://github.com/Pedronsjaja/gaia-humanoid-structure/blob/main/docs/modelo-gaia.md) · [Autonomia](https://github.com/Pedronsjaja/gaia-humanoid-simulation/blob/main/docs/simulacao/autonomia.md) · [CBR Humanoid](https://github.com/Pedronsjaja/gaia-humanoid-structure/blob/main/docs/competicao/README.md).

A bancada serial é a base para a futura integração ROS/LX-225. O adaptador OP3 de simulação não implementa essa ponte e não substitui a caracterização dos atuadores reais.
