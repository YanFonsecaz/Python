# Guia de Uso: Processamento de Itens

## Como Usar a Funcionalidade de Processamento de Itens

### Acesso à Funcionalidade

1. **Navegue até a aplicação**: Abra seu navegador e acesse `http://localhost:5173`

2. **Localize o menu**: No menu lateral esquerdo, procure pela opção **"Processar Item"** com o ícone de engrenagem (⚙️)

3. **Clique no link**: Clique em "Processar Item" para acessar a página de processamento

### Processando um Item

#### Passo 1: Inserir ID do Item
- Na página "Processar Item", você verá um campo de entrada
- Digite o **ID numérico** do item que deseja processar
- Exemplo: `10`, `25`, `100`

#### Passo 2: Executar Processamento
- Clique no botão **"Processar Item"**
- O sistema iniciará o processamento (você verá um spinner de carregamento)
- Aguarde a conclusão da operação

#### Passo 3: Visualizar Resultado
- **Sucesso**: Os dados processados aparecerão em uma caixa verde
- **Erro**: Você será redirecionado para uma página de erro com detalhes

### Estados da Interface

#### 🔄 Carregamento
- **Indicador**: Spinner animado
- **Botão**: Fica desabilitado com texto "Processando..."
- **Ação**: Aguarde a conclusão

#### ✅ Sucesso
- **Indicador**: Caixa verde com os dados
- **Conteúdo**: ID do item e resultado do processamento
- **Ação**: Você pode processar outro item ou limpar os dados

#### ❌ Erro
- **Indicador**: Redirecionamento para página de erro
- **Conteúdo**: Mensagem de erro detalhada
- **Ações**: "Tentar Novamente" ou "Voltar ao Início"

### Funcionalidades Disponíveis

#### Limpar Dados
- Clique no botão **"Limpar"** para:
  - Limpar o campo de entrada
  - Remover resultados exibidos
  - Resetar o estado da aplicação

#### Processar Novo Item
- Após um processamento bem-sucedido
- Digite um novo ID no campo
- Clique em "Processar Item" novamente

### Exemplos de Uso

#### Exemplo 1: Processamento Bem-sucedido
```
1. Digite: 10
2. Clique: "Processar Item"
3. Resultado: "Dados processados para o item 10. Timestamp: 2025-09-28T21:32:17"
```

#### Exemplo 2: Tratamento de Erro
```
1. Digite: -5 (ID inválido)
2. Clique: "Processar Item"
3. Resultado: Redirecionamento para página de erro
```

### Dicas de Uso

#### ✅ Boas Práticas
- Use apenas **números positivos** como ID
- Aguarde o processamento completo antes de nova tentativa
- Verifique a conexão com o servidor se houver erros

#### ⚠️ Limitações
- IDs devem ser números inteiros
- Não use caracteres especiais ou letras
- Aguarde o processamento anterior terminar

### Solução de Problemas

#### Problema: Página não carrega
**Solução**: 
- Verifique se o servidor React está rodando (`http://localhost:5173`)
- Atualize a página (F5)

#### Problema: Erro de conexão
**Solução**:
- Verifique se o servidor Flask está rodando (`http://localhost:5001`)
- Confirme as configurações de rede

#### Problema: Processamento lento
**Solução**:
- Aguarde até 10 segundos (timeout configurado)
- Verifique a carga do servidor

### Navegação

#### Voltar ao Menu Principal
- Clique no logo ou título da aplicação
- Use o menu lateral para navegar para outras seções

#### Acessar Outras Funcionalidades
- **Dashboard**: Visão geral do sistema
- **Auditorias**: Funcionalidades de auditoria SEO
- **Relatórios**: Visualização de dados
- **Configurações**: Ajustes do sistema

---

**Suporte**: Em caso de dúvidas, consulte a documentação técnica ou entre em contato com o administrador do sistema.

**Versão**: 1.0
**Última Atualização**: 28/09/2025