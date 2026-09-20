# Bibliotecas, versões e validação

[Índice](README.md)

Consulta e inspeção de fontes: **20/09/2026**.

## Fontes ROBOTIS

| Fonte | O que estudar | Uso neste laboratório |
| --- | --- | --- |
| [OP3 Hardware](https://emanual.robotis.com/docs/en/platform/op3/hardware/#hardware) | Montagem, cobertura e eletrônica | Referência mecânica |
| [OP3 Simulation](https://emanual.robotis.com/docs/en/platform/op3/simulation/#simulation) | Gazebo/Webots, abas ROS 2 e ROS 1 | Referência do fabricante |
| [ROBOTIS-OP3-Common](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/tree/jazzy-devel) | Modelo, malhas e inércias | Dependência baixada por vcs |
| [ROBOTIS-OP3-Simulations](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-Simulations/tree/jazzy-devel) | Lançadores Gazebo/Webots e ponte | Inspecionado, não necessário para o laboratório Gaia |
| [ROBOTIS-OP3](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3/tree/jazzy-devel) | Manager, cinemática, equilíbrio, marcha e movimentos | Estudo posterior |
| [ROBOTIS-OP3-msgs](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-msgs) | Interfaces dos módulos OP3 | Estudo posterior |
| [ROBOTIS-Framework](https://github.com/ROBOTIS-GIT/ROBOTIS-Framework) | Dispositivos, controle e módulos | Referência de arquitetura |
| [ROBOTIS-Framework-msgs](https://github.com/ROBOTIS-GIT/ROBOTIS-Framework-msgs) | Interfaces do framework | Referência |
| [ROBOTIS-Math](https://github.com/ROBOTIS-GIT/ROBOTIS-Math) | Matemática robótica | Verificar branch/dependências antes de reutilizar |
| [DynamixelSDK](https://github.com/ROBOTIS-GIT/DynamixelSDK) | Comunicação DYNAMIXEL | Não controla diretamente LX-225 |

Não há promessa de que clonar todos esses repositórios e executar colcon produza uma pilha completa funcional. O caminho introdutório instala apenas `op3_description` e o adaptador Gaia, com dependências ROS declaradas.

## Revisões inspecionadas

| Repositório | Branch | SHA |
| --- | --- | --- |
| ROBOTIS-OP3-Common | jazzy-devel | `6f7d56ccef6f78061925c56c6bd9d134d243f911` |
| ROBOTIS-OP3-Simulations | jazzy-devel | `7a07512e373f70fbda8fd536269948b06dc42b37` |
| ROBOTIS-OP3 | jazzy-devel | `50f2367839d4aa9cd6f29ff1fb8ff504fc836655` |

Evidência do ajuste necessário: no [Xacro principal fixado](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/blob/6f7d56ccef6f78061925c56c6bd9d134d243f911/op3_description/urdf/robotis_op3.urdf.xacro), a inclusão `robotis_op3.ros2.gazebo.xacro` está comentada, e esse arquivo não está presente na árvore da revisão. Já o [launch de simulação](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-Simulations/blob/7a07512e373f70fbda8fd536269948b06dc42b37/op3_gazebo_ros2/launch/robot_sim.launch.py) tenta carregar controladores.

O adaptador [model.py](../../ros2/gaia_op3_sim/gaia_op3_sim/model.py) usa somente geometria/juntas/inércias do modelo oficial e acrescenta sua configuração. Ele rejeita mudanças inesperadas no conjunto de juntas e modelos que já tragam `ros2_control`, para exigir revisão em vez de duplicar plugins.

O [package.xml de cinemática](https://github.com/ROBOTIS-GIT/ROBOTIS-OP3/blob/50f2367839d4aa9cd6f29ff1fb8ff504fc836655/op3_kinematics_dynamics/package.xml) ainda declara `roscpp` nessa branch ROS 2. Portanto, a instalação do manager/marcha fica fora da receita introdutória e demanda auditoria de dependências.

## Como manter as versões

O manifesto [op3.repos](../../simulation/op3.repos) fixa o Common por SHA. Para atualizar: revisar diferenças, rodar testes, testar Gazebo, registrar resultados e só então alterar o SHA. Não usar `git pull` aleatoriamente em uma aula que depende de revisão fixa.

Modelos são baixados do fabricante e mantêm suas licenças. O código novo em `ros2/gaia_op3_sim` tem [licença MIT](../../ros2/gaia_op3_sim/LICENSE), limitada a esse pacote; ela não altera a licença dos CADs já existentes ou dos repositórios ROBOTIS.

## Estado de validação

A expansão do modelo oficial e cinco testes do adaptador passaram localmente. A bancada tem 47 testes aprovados com serial simulada.

A automação Linux compila e verifica o modelo, sem executar a física/renderização. A execução gráfica, os sensores em runtime e o desempenho ainda precisam ser validados nos PCs da equipe. Marcha autônoma e interface ROS/LX-225 não estão implementadas.

Consulte o [registro de validação e ficha de ensaio](validacao.md) e o [resultado da automação](https://github.com/Pedronsjaja/gaia-humanoid-robot/actions/workflows/simulation.yml).

## Referências da plataforma

[Ubuntu 24.04](https://releases.ubuntu.com/24.04/), [ROS Jazzy](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html), [Gazebo Harmonic](https://gazebosim.org/docs/harmonic/ros_installation/), [gz_ros2_control](https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html) e [sensores Gazebo](https://gazebosim.org/docs/harmonic/sensors/).
