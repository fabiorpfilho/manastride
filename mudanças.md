### Relatório: Resumo das Alterações Realizadas no Código do Jogo

Este relatório detalha as mudanças realizadas no código do jogo, com base na comparação entre a versão original do `Level` e as versões atuais de `Level`, `ObjectFactory`, e `EntityManager`, além das modificações discutidas ao longo da conversa. As alterações focam na refatoração para maior modularidade, correção de bugs, e implementação de novos comportamentos, com ênfase nos tópicos **Tópico 1: Fundamentos de Projeto Orientado a Objetos**, **Tópico 7: Padrões de Projeto**, **Tópico 8: Prática de Projeto, Análise Crítica e Melhoria Contínua**, e **Princípios SOLID**. As seções abaixo descrevem as mudanças, as versões finais de cada classe, os objetivos, e os tópicos aplicados.

---

#### 1. Criação do `ObjectFactory` (object_factory.py)
**Objetivo**: Centralizar a criação de objetos do jogo (`Player`, `HammerBot`, `Rune`, `Door`, `Terrain`) em uma classe modular, eliminando a lógica de criação direta no `Level` e facilitando a extensibilidade para novos tipos de objetos, como chefes para uma arena.

**Mudanças Principais**:
- Criada a classe `ObjectFactory` com um dicionário `object_map` que mapeia pares `(type, name)` ou `(type, None)` a métodos de criação específicos (`_create_player`, `_create_hammer_bot`, `_create_rune`, `_create_door`).
- Método `create_object` processa elementos XML do Tiled ou dicionários, delegando a criação aos métodos apropriados.
- Método `_create_player` evita recriação do jogador, mantendo uma única instância e atualizando sua posição com `update_player_position`.
- Métodos `_create_hammer_bot`, `_create_rune`, e `_create_door` extraem propriedades do XML (ex.: posição, tamanho, `rune_type`, `player_spawn`) para criar objetos.
- Método `create_terrain` cria terrenos diretamente, usado para tiles do mapa.
- Adicionado suporte para evitar recriação de runas principais já coletadas e carregar imagens específicas para runas menores.

**Tópicos Aplicados**:
- **Tópico 1 (OO)**:
  - **Encapsulamento**: Centraliza a criação de objetos em `ObjectFactory`, isolando a lógica de construção do `Level`.
  - **Coesão**: Cada método (`_create_player`, `_create_hammer_bot`, etc.) tem uma única responsabilidade.
- **Tópico 7 (Padrões)**:
  - **Factory Pattern**: O `object_map` mapeia tipos e nomes a métodos de criação, permitindo extensibilidade.
  - **Strategy Pattern**: Usado como inspiração no mapeamento de funções em `object_map`, que delega a criação a métodos específicos.
- **SOLID**:
  - **S**: `ObjectFactory` é responsável apenas pela criação de objetos.
  - **O**: Extensível para novos tipos de objetos via `object_map`.
  - **L**: Objetos criados são tratados polimorficamente em `Level` e `EntityManager`.

---

#### 2. Adaptação do `Level` para Usar `ObjectFactory` e `EntityManager` (level.py)
**Objetivo**: Refatorar `Level` para delegar a criação de objetos ao `ObjectFactory` e a gestão de entidades dinâmicas ao `EntityManager`, simplificando a lógica, corrigindo o bug de portas sendo tratadas como entidades dinâmicas, e melhorando a modularidade.

**Mudanças Principais (Comparação com a Versão Original)**:
- **Remoção de Atributos**:
  - Original: `player`, `dynamic_objects`, e `enemies` gerenciavam entidades diretamente.
  - Atual: Substituídos por `entity_manager`, que delega a gestão de entidades dinâmicas.
- **Inicialização**:
  - Original: Criava `SpellSystem` e `AssetLoader` diretamente, sem `ObjectFactory`.
  - Atual: Inicializa `ObjectFactory` e `EntityManager` em `__init__`, integrando-os com `spell_system` e `asset_loader`.
- **Método `_process_objects`**:
  - Original: Criava objetos (`Player`, `HammerBot`, `Rune`, `Door`) diretamente, processando XML manualmente e adicionando portas a `dynamic_objects` incorretamente.
  - Atual: Usa `entity_manager.object_factory.create_object` para criar objetos, adicionando entidades dinâmicas (`Player`, `HammerBot`, `Rune`) ao `entity_manager` com `add_entity` e objetos estáticos (`Door`) a `static_objects`.
- **Método `_process_tilemap`**:
  - Original: Criava `Terrain` diretamente.
  - Atual: Usa `entity_manager.object_factory.create_terrain` para criar terrenos.
- **Método `update`**:
  - Original: Iterava `dynamic_objects` com verificações `isinstance` para atualizar `Player`, `HammerBot`, `Rune`, e gerenciava projéteis/escudos diretamente.
  - Atual: Delega atualizações ao `entity_manager.update`, que usa `update_map` para atualizações específicas, simplificando a lógica e gerenciando projéteis/escudos.
- **Método `reset`**:
  - Original: Reposicionava o jogador e recriava `enemies` diretamente.
  - Atual: Usa `entity_manager.object_factory` para criar um novo `HammerBot` e reposicionar o jogador, recriando `EntityManager` para reiniciar entidades.

**Tópicos Aplicados**:
- **Tópico 1 (OO)**:
  - **Encapsulamento**: Delega criação de objetos ao `ObjectFactory` e gestão de entidades ao `EntityManager`, reduzindo acoplamento.
  - **Coesão**: Métodos como `_process_objects` focam na inicialização, enquanto `update` orquestra o fluxo.
- **Tópico 7 (Padrões)**:
  - **Factory Pattern**: Usa `ObjectFactory` para criar objetos em `_process_objects` e `_process_tilemap`.
  - **Strategy Pattern**: Atualizações delegadas ao `EntityManager.update` com `update_map`.
- **SOLID**:
  - **S**: `Level` orquestra o fluxo; `ObjectFactory` cria objetos; `EntityManager` gerencia entidades.
  - **O**: Extensível para novos níveis e objetos.
  - **L**: Objetos são tratados polimorficamente via `EntityManager`.

---

#### 3. Criação do `EntityManager` (entity_manager.py)
**Objetivo**: Refatorar a lógica de atualização de entidades dinâmicas do `Level.update` para uma classe `EntityManager`, movendo a geração de runas menores e implementando a manutenção de corpos de inimigos em `all_sprites`.

**Mudanças Principais**:
- Criada a classe `EntityManager` com `update_map` para atualizar entidades (`Player`, `HammerBot`, `Rune`) via métodos específicos.
- Métodos `add_entity` e `remove_entity` gerenciam entidades dinâmicas e inimigos.
- Lógica de geração de runas menores movida para `_generate_minor_rune`, usando `ObjectFactory`.
- Método `update` substitui o loop com `isinstance` do `Level`, gerenciando projéteis e escudos.
- Adicionados `get_player` e `check_completion` para acessar o jogador e verificar conclusão.
- Modificado `remove_entity` para manter inimigos em `all_sprites`, com corpos visíveis como sprites estáticos.

#### Impacto no Jogo
- **Funcionalidade**: Modularidade aumentada com `ObjectFactory` e `EntityManager`.
- **Robustez**: Logging e validações melhoram depuração.
- **Extensibilidade**: Suporta adição de novos objetos e níveis (ex.: arena).


#### Sugestões para o Futuro
- **LevelArena**: Criar classe para gerenciar waves de inimigos.
- **SINGLETON**: Implementar SINGLETON em classes em que só é necessário e recomendado ter uma instância para evitar a possibilidade de conflitos caso acidentalmente seja gerado outra, como `EntityManager` e `CollisionManager`
- **Retirar importação de classes de único uso**: Classes como `ObjectFactory` onde só é chamada breviamente para a uma função e depois não é mais usada não precisam ser instnaciadas todo o tempo, modificar ela para ser estatica e publicar seus métodos para outras classes acessarem sem a necessidade de importação e instanciação continua
