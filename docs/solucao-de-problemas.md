# Solução de problemas

[Voltar ao README](../README.md) · [Instalação](instalacao.md) · [Comandos](uso.md)

Comece com **um servo, um cabo e uma fonte**, sem movimento. Mude uma variável por vez. A tabela descreve hipóteses de diagnóstico, não defeitos confirmados de todas as placas.

## Instalação e conexão

| Sintoma | Possível causa | Como verificar e corrigir |
| --- | --- | --- |
| Python não encontrado | PATH ou instalação | Abra novo terminal; tente o launcher `py` se instalado; confira instalação do Python |
| `No module named serial` ou `matplotlib` | Ambiente errado/dependência ausente | Use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Activate.ps1 bloqueado | Política do PowerShell | Execute diretamente o Python de .venv |
| COM não aparece | Cabo só de carga, driver ausente ou USB com falha | Troque por cabo de dados, verifique Gerenciador de Dispositivos e [driver](softwares-e-drivers.md) |
| Access denied / PermissionError | COM ocupada ou permissão | Feche softwares/monitores; no Linux confira grupo da porta |
| Porta não existe | COM mudou ou USB desconectou | Execute `python -m serial.tools.list_ports -v` novamente |
| Várias portas disponíveis | Seleção automática ambígua | Informe `--port COM7` com a porta real |
| Gráfico não abre | Ambiente sem interface gráfica ou backend indisponível | Teste sem `--live` e confira o arquivo em resultados/; use ambiente desktop para a janela |

## Comunicação e movimento

| Sintoma | Possível causa | Próximo passo |
| --- | --- | --- |
| Nenhum ID encontrado | Falta de alimentação externa, modo USB incorreto, cabo ou ID | Confira alimentação, jumpers pelo manual da revisão e faça `--scan` com um servo |
| COM abre, servo não responde | Conversor USB funciona, mas barramento não | Confira GND, sinal, conector, fonte e protocolo; LX-225 usa 115200 baud |
| Menos servos que o esperado | ID duplicado, cabo interrompido ou servo sem resposta | Consulte cada servo separadamente; configure IDs exclusivos |
| Leituras intermitentes/pacotes inválidos | Ruído, mau contato, queda de tensão, IDs duplicados | Reduza ao conjunto mínimo e acrescente um servo/cabo por vez |
| Tensão cai durante movimento | Fonte, cabos ou conectores insuficientes; carga elevada | Interrompa; confira tensão junto ao servo sob carga e dimensionamento; aumentar delta não resolve |
| Alvo rejeitado | Fora de 0–240° ou dos limites internos | Leia a posição atual e confira o deslocamento; respeite também os limites mecânicos |
| Modo motor detectado | Servo configurado para rotação contínua | Consulte o modo e configure modo de posição pelo software apropriado antes de repetir |
| Torque desligado | Configuração ou proteção do servo | A leitura não habilita torque; o teste só o habilita quando há movimento solicitado e alvo confirmado |
| Eixo não gira apesar de leitura | Carga, obstrução, limite, torque/proteção | Use diagnóstico abaixo, confira alimentação e mecânica; não force o eixo |
| Temperatura elevada | Sobrecarga, travamento ou esforço contínuo | Interrompa o ensaio e investigue carga/atrito antes de repetir |
| Falha ao confirmar alvo | Servo não confirmou o comando enviado | Não repita movimentos amplos; confira comunicação e compatibilidade |
| Falha em `--synchronized` | Preparo não confirmado | Não envie novo broadcast; reinicie a alimentação para restabelecer estado conhecido |
| ID mudou, cadastro não atualizou | Gravação local ou confirmação falhou | Consulte ID antigo e novo; uma falha do JSON não desfaz a alteração física |

A busca conta **endereços que responderam**, não garante a quantidade física. A verificação de tensão por software depende das leituras e não substitui alimentação corretamente dimensionada.

## Diagnóstico somente de leitura

Execute na raiz, com ambiente virtual ativo, substituindo porta e ID:

```powershell
python tools/diagnose_servo.py --port COM7 --id 1
```

O diagnóstico consulta ID, posição, tensão, temperatura, modo, torque, limites e alvos imediato/preparado. Ele não move nem grava configurações. `SEM RESPOSTA VALIDA` indica que aquela consulta falhou; isoladamente, não comprova servo danificado.

Se uma leitura comum funciona e só um comando avançado falha, registre qual comando falhou antes de concluir que há problema elétrico. Confira os [manuais e protocolo](datasheets/README.md).

## CAD e impressão

| Sintoma | Verificação |
| --- | --- |
| Montagem SolidWorks pede peças | Extraia a pasta inteira; mantenha SLDASM, SLDPRT e imagens juntos; procure os nomes originais na mesma pasta |
| Não consigo editar IPT | Use Inventor compatível; para os quatro suportes Gaia há STEP |
| Peça muito grande/pequena no fatiador | STL não declara unidade; confira milímetros e compare medidas com CAD/servo |
| Furos ou suporte não encaixam | Confira escala, tolerância de impressão e variante; não aumente o torque do servo para compensar |
| Semaforo frame sem STL | Só há IPT desse modelo no material fornecido; exportação permanece pendente |

## Informações para relatar uma falha

Inclua revisão da BusLinker, modelo/IDs dos servos, sistema e versão do Python, COM, tensão nominal da fonte, comando completo e saída do terminal. Descreva se ocorre com um servo isolado ou só no conjunto e o resultado das leituras.

Os testes em `tests/` usam serial simulada. Sua aprovação não comprova a montagem física. `Ctrl+C` tenta parar movimentos em execução, mas perda de comunicação pode impedir a parada; fechar a porta não remove torque.
