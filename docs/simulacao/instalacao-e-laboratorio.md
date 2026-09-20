# Instalar o simulador e colocar o OP3 no cenário

[Índice](README.md) · Próximo: [modelo Gaia](modelo-gaia.md)

Pré-requisito: Ubuntu **24.04**, ROS 2 **Jazzy** e teste talker/listener aprovado pelo [guia de ambiente](https://github.com/Pedronsjaja/gaia-ros2-ubuntu24). Execute no Bash do Ubuntu. Não há hardware físico nesta aula.

**Estado do roteiro:** compilação, modelo, sensores e trajetória da cabeça aprovados em Linux/Gazebo sem janela. Inspeção visual e desempenho no seu computador ainda precisam ser verificados. Veja a [evidência e ficha de validação](validacao.md).

## 1. Instalar Gazebo e integração

```bash
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install ros-jazzy-ros-gz ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
  ros-jazzy-xacro ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-robot-state-publisher ros-jazzy-rviz2 \
  ros-jazzy-rqt-image-view ros-dev-tools python3-pytest
```

Esses pacotes usam a combinação Jazzy/Harmonic. Não adicione Gazebo Classic nem misture instruções Humble/Ubuntu 22.04. Referências: [instalação Gazebo/ROS](https://gazebosim.org/docs/harmonic/ros_installation/) e [gz_ros2_control](https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html).

## 2. Baixar o projeto e o modelo oficial

Use um workspace novo para esta aula:

```bash
mkdir -p ~/gaia_ws/src
cd ~/gaia_ws/src
git clone https://github.com/Pedronsjaja/gaia-humanoid-robot.git
cd ~/gaia_ws
vcs import src < src/gaia-humanoid-robot/simulation/op3.repos
```

A importação baixa `ROBOTIS-OP3-Common` na revisão registrada. A geometria e as inércias vêm de `op3_description`; o pacote Gaia adiciona o cenário e a configuração de simulação. Se a pasta já existe, não clone por cima: confira `git status` e use um workspace novo ou atualize conscientemente.

Inicialize rosdep, se necessário, e resolva dependências:

```bash
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro jazzy -y
colcon build --symlink-install --packages-up-to gaia_op3_sim
source install/setup.bash
ros2 pkg prefix op3_description
ros2 pkg prefix gaia_op3_sim
```

Os dois últimos comandos devem retornar caminhos em `~/gaia_ws/install`. `colcon` detecta os pacotes dentro de `ros2/`; os scripts Python de bancada na raiz não são pacotes ROS.

## 3. Preparar cada terminal da aula

Repita em todos os terminais que vão participar da simulação:

```bash
source /opt/ros/jazzy/setup.bash
source ~/gaia_ws/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
```

Não execute simultaneamente outros simuladores no mesmo domínio. `LOCALHOST` mantém este exercício no computador/VM.

## 4. Abrir o mundo e inserir o robô

No terminal A:

```bash
ros2 launch gaia_op3_sim lab.launch.py
```

**Resultado esperado:** janela do Gazebo com chão, caixa vermelha e OP3 suspenso. O comando já expande o Xacro, publica `robot_description`, insere o modelo e inicia controladores e ponte de sensores. Não é necessário arrastar um STL para a cena.

Espere carregar. No terminal B:

```bash
ros2 control list_controllers
ros2 topic echo /clock --once
ros2 topic echo /joint_states --once
```

Espere `joint_state_broadcaster` e `joint_trajectory_controller` em **active** e posições para 20 juntas. `/clock` é o relógio do mundo virtual.

Para executar sem a janela, útil em uma VM:

```bash
ros2 launch gaia_op3_sim lab.launch.py gui:=false
```

Encerre a execução anterior antes de iniciar outra. Câmera ainda precisa de renderização; modo sem janela não elimina os requisitos gráficos de EGL/Mesa/GPU. Em host sem aceleração adequada, teste `LIBGL_ALWAYS_SOFTWARE=1` antes do comando, aceitando desempenho inferior.

## 5. Primeiro movimento: cabeça

Com os controladores ativos e a base **presa**, publique uma trajetória parcial:

```bash
ros2 topic pub --once /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{joint_names: ['head_pan'], points: [{positions: [0.15], time_from_start: {sec: 2}}]}"
```

O alvo é **0,15 radianos absolutos**, aproximadamente 8,6°, no referencial da junta OP3. Não é deslocamento relativo nem valor em graus da bancada LX-225. O controlador permite trajetórias parciais neste laboratório; as demais juntas mantêm seus alvos.

Observe:

```bash
ros2 topic echo /joint_states --once
```

Procure `head_pan` no vetor `name` e o elemento correspondente em `position`. Para retornar a zero, repita a publicação com `positions: [0.0]`.

Este exercício verifica a cadeia **mensagem → controlador → junta simulada → leitura**. Não é algoritmo de marcha.

## 6. Ver câmera e IMU

```bash
ros2 topic list
ros2 topic echo /gaia/imu --once --qos-reliability best_effort
ros2 topic hz /gaia/camera/image_raw
```

Ctrl+C encerra a medição de taxa. Para a imagem:

```bash
ros2 run rqt_image_view rqt_image_view
```

Selecione `/gaia/camera/image_raw`. Há também `/gaia/camera/camera_info`. A IMU está no tronco e a câmera é uma configuração didática na cabeça; as taxas configuradas são 50 Hz e 15 Hz, respectivamente, em tempo de simulação. A taxa observada pode ser menor que isso no relógio real se o simulador estiver lento.

## 7. Visualizar em RViz e gravar evidências

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Use `world` como **Fixed Frame** no modo preso; adicione **RobotModel** com `/robot_description` e **TF**. O Gazebo calcula a física; RViz exibe o estado publicado. Em base livre, a pose global da base exigirá TF/estimativa de estado; não confunda a árvore de juntas com localização global.

Para um registro curto:

```bash
mkdir -p ~/gaia_registros
cd ~/gaia_registros
ros2 bag record /clock /joint_states /gaia/imu /gaia/camera/camera_info
```

Encerre com Ctrl+C. Adicione a imagem apenas quando necessário, pois ela aumenta bastante o volume. Anote data, revisão do manifesto, hardware, taxa observada e comandos. Dados de experimento não devem ser versionados como código.

## 8. Encerrar e avançar

Encerre as ferramentas e o launch com Ctrl+C. Para estudar quedas/contato, após dominar o laboratório:

```bash
ros2 launch gaia_op3_sim lab.launch.py fixed_base:=false
```

Esse modo remove o suporte; **não há controlador de equilíbrio**, e uma queda não implica erro de instalação. Não use ganhos ou esforços idealizados desse modelo para dimensionar o Gaia.

## Se algo falhar

| Sintoma | Verificação |
| --- | --- |
| Pacote não encontrado | Source do install e resultado da compilação |
| Xacro reclama das juntas | Revisão do modelo mudou; use o manifesto, não silencie o erro do adaptador |
| Controller manager não aparece | Log do plugin gz_ros2_control e pacotes Jazzy; spawner espera até 120 s |
| Controlador inactive | `ros2 control list_hardware_interfaces` e logs; não inicie outro controlador na mesma interface |
| Malhas não aparecem | Confirme op3_description e GZ_SIM_RESOURCE_PATH; não mova meshes isoladamente |
| Clock não avança | Mundo pausado, processo encerrado ou ponte com falha |
| Câmera ausente | Logs Sensors/Ogre/EGL e tópico Gazebo; conferir ponte e aceleração gráfica |
| RobotModel desalinhado/TF antigo | use_sim_time e Fixed Frame; não abrir outro joint_state_publisher |
| Trajetória sem efeito | Controlador active, nome da junta, radianos e presença de assinante |
| Robô cai | Confira fixed_base; modo livre precisa de equilíbrio próprio |

A instalação gráfica e a dinâmica devem ser verificadas nos PCs da equipe. Consulte o [registro de validação](referencias.md) antes de tratar a bancada virtual como validada.
