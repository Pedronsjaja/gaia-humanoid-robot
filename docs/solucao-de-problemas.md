# SoluÃ§Ã£o de problemas

[Voltar ao README](../README.md) Â· [InstalaÃ§Ã£o](instalacao.md) Â· [Comandos](uso.md)

Comece com **um servo, um cabo e uma fonte**, sem movimento. Mude uma variÃ¡vel por vez. A tabela descreve hipÃ³teses de diagnÃ³stico, nÃ£o defeitos confirmados de todas as placas.

## InstalaÃ§Ã£o e conexÃ£o

| Sintoma | PossÃ­vel causa | Como verificar e corrigir |
| --- | --- | --- |
| Python nÃ£o encontrado | PATH ou instalaÃ§Ã£o | Abra novo terminal; tente o launcher `py` se instalado; confira instalaÃ§Ã£o do Python |
| `No module named serial` ou `matplotlib` | Ambiente errado/dependÃªncia ausente | Use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Activate.ps1 bloqueado | PolÃ­tica do PowerShell | Execute diretamente o Python de .venv |
| COM nÃ£o aparece | Cabo sÃ³ de carga, driver ausente ou USB com falha | Troque por cabo de dados, verifique Gerenciador de Dispositivos e [driver](softwares-e-drivers.md) |
| Access denied / PermissionError | COM ocupada ou permissÃ£o | Feche softwares/monitores; no Linux confira grupo da porta |
| Porta nÃ£o existe | COM mudou ou USB desconectou | Execute `python -m serial.tools.list_ports -v` novamente |
| VÃ¡rias portas disponÃ­veis | SeleÃ§Ã£o automÃ¡tica ambÃ­gua | Informe `--port COM7` com a porta real |
| GrÃ¡fico nÃ£o abre | Ambiente sem interface grÃ¡fica ou backend indisponÃ­vel | Teste sem `--live` e confira o arquivo em resultados/; use ambiente desktop para a janela |

## ComunicaÃ§Ã£o e movimento

| Sintoma | PossÃ­vel causa | PrÃ³ximo passo |
| --- | --- | --- |
| Nenhum ID encontrado | Falta de alimentaÃ§Ã£o externa, modo USB incorreto, cabo ou ID | Confira alimentaÃ§Ã£o, jumpers pelo manual da revisÃ£o e faÃ§a `--scan` com um servo |
| COM abre, servo nÃ£o responde | Conversor USB funciona, mas barramento nÃ£o | Confira GND, sinal, conector, fonte e protocolo; LX-225 usa 115200 baud |
| Menos servos que o esperado | ID duplicado, cabo interrompido ou servo sem resposta | Consulte cada servo separadamente; configure IDs exclusivos |
| Leituras intermitentes/pacotes invÃ¡lidos | RuÃ­do, mau contato, queda de tensÃ£o, IDs duplicados | Reduza ao conjunto mÃ­nimo e acrescente um servo/cabo por vez |
| TensÃ£o cai durante movimento | Fonte, cabos ou conectores insuficientes; carga elevada | Interrompa; confira tensÃ£o junto ao servo sob carga e dimensionamento; aumentar delta nÃ£o resolve |
| Alvo rejeitado | Fora de 0â€“240Â° ou dos limites internos | Leia a posiÃ§Ã£o atual e confira o deslocamento; respeite tambÃ©m os limites mecÃ¢nicos |
| Modo motor detectado | Servo configurado para rotaÃ§Ã£o contÃ­nua | Consulte o modo e configure modo de posiÃ§Ã£o pelo software apropriado antes de repetir |
| Torque desligado | ConfiguraÃ§Ã£o ou proteÃ§Ã£o do servo | A leitura nÃ£o habilita torque; o teste sÃ³ o habilita quando hÃ¡ movimento solicitado e alvo confirmado |
| Eixo nÃ£o gira apesar de leitura | Carga, obstruÃ§Ã£o, limite, torque/proteÃ§Ã£o | Use diagnÃ³stico abaixo, confira alimentaÃ§Ã£o e mecÃ¢nica; nÃ£o force o eixo |
| Temperatura elevada | Sobrecarga, travamento ou esforÃ§o contÃ­nuo | Interrompa o ensaio e investigue carga/atrito antes de repetir |
| Falha ao confirmar alvo | Servo nÃ£o confirmou o comando enviado | NÃ£o repita movimentos amplos; confira comunicaÃ§Ã£o e compatibilidade |
| Falha em `--synchronized` | Preparo nÃ£o confirmado | NÃ£o envie novo broadcast; reinicie a alimentaÃ§Ã£o para restabelecer estado conhecido |
| ID mudou, cadastro nÃ£o atualizou | GravaÃ§Ã£o local ou confirmaÃ§Ã£o falhou | Consulte ID antigo e novo; uma falha do JSON nÃ£o desfaz a alteraÃ§Ã£o fÃ­sica |

A busca conta **endereÃ§os que responderam**, nÃ£o garante a quantidade fÃ­sica. A verificaÃ§Ã£o de tensÃ£o por software depende das leituras e nÃ£o substitui alimentaÃ§Ã£o corretamente dimensionada.

## DiagnÃ³stico somente de leitura

Execute na raiz, com ambiente virtual ativo, substituindo porta e ID:

```powershell
python tools/diagnose_servo.py --port COM7 --id 1
```

O diagnÃ³stico consulta ID, posiÃ§Ã£o, tensÃ£o, temperatura, modo, torque, limites e alvos imediato/preparado. Ele nÃ£o move nem grava configuraÃ§Ãµes. `SEM RESPOSTA VALIDA` indica que aquela consulta falhou; isoladamente, nÃ£o comprova servo danificado.

Se uma leitura comum funciona e sÃ³ um comando avanÃ§ado falha, registre qual comando falhou antes de concluir que hÃ¡ problema elÃ©trico. Confira os [manuais e protocolo](datasheets/README.md).

## CAD e impressÃ£o

| Sintoma | VerificaÃ§Ã£o |
| --- | --- |
| Montagem SolidWorks pede peÃ§as | Extraia a pasta inteira; mantenha SLDASM, SLDPRT e imagens juntos; procure os nomes originais na mesma pasta |
| NÃ£o consigo editar IPT | Use Inventor compatÃ­vel; para os quatro suportes Gaia hÃ¡ STEP |
| PeÃ§a muito grande/pequena no fatiador | STL nÃ£o declara unidade; confira milÃ­metros e compare medidas com CAD/servo |
| Furos ou suporte nÃ£o encaixam | Confira escala, tolerÃ¢ncia de impressÃ£o e variante; nÃ£o aumente o torque do servo para compensar |
| Semaforo frame sem STL | SÃ³ hÃ¡ IPT desse modelo no material fornecido; exportaÃ§Ã£o permanece pendente |

## InformaÃ§Ãµes para relatar uma falha

Inclua revisÃ£o da BusLinker, modelo/IDs dos servos, sistema e versÃ£o do Python, COM, tensÃ£o nominal da fonte, comando completo e saÃ­da do terminal. Descreva se ocorre com um servo isolado ou sÃ³ no conjunto e o resultado das leituras.

Os testes em `tests/` usam serial simulada. Sua aprovaÃ§Ã£o nÃ£o comprova a montagem fÃ­sica. `Ctrl+C` tenta parar movimentos em execuÃ§Ã£o, mas perda de comunicaÃ§Ã£o pode impedir a parada; fechar a porta nÃ£o remove torque.
