<script setup>
import { RouterLink } from 'vue-router'

const atalhos = [
  { tecla: 'Tab', acao: 'Avança para o próximo item (campo, link ou botão)' },
  { tecla: 'Shift + Tab', acao: 'Volta para o item anterior' },
  { tecla: 'Enter', acao: 'Ativa o link ou botão em foco' },
  { tecla: 'Espaço', acao: 'Marca caixas de seleção e aciona botões' },
  { tecla: 'Setas', acao: 'Percorre as opções de uma lista suspensa' },
  { tecla: 'Esc', acao: 'Fecha a caixa de confirmação aberta' },
  { tecla: 'Ctrl + / Ctrl -', acao: 'Aumenta ou diminui o zoom da página' },
]
</script>

<template>
  <article class="pagina">
    <header>
      <h1>Declaração de Acessibilidade</h1>
      <p class="texto-suave">
        Compromisso com a Lei Brasileira de Inclusão (Lei 13.146/2015) e com as
        diretrizes WCAG 2.1, nível AA.
      </p>
    </header>

    <section aria-labelledby="compromisso">
      <h2 id="compromisso">Nosso compromisso</h2>
      <p>
        O Acervo Edu IA é uma plataforma educacional, e material de estudo precisa chegar a
        todas as pessoas. Por isso a interface foi construída para funcionar com leitores de
        tela, apenas pelo teclado e com zoom ampliado — não como um ajuste posterior, mas
        como parte do desenvolvimento.
      </p>
      <p>
        O art. 63 da Lei 13.146/2015 torna obrigatória a acessibilidade em sites, e o
        Decreto 9.296/2018 reforça essa exigência para serviços públicos e educacionais.
      </p>
    </section>

    <section aria-labelledby="recursos">
      <h2 id="recursos">O que já está implementado</h2>
      <ul>
        <li>
          <strong>Navegação por teclado completa:</strong> todos os campos, botões e links
          são alcançáveis por <kbd>Tab</kbd>, na ordem em que aparecem na tela.
        </li>
        <li>
          <strong>Foco sempre visível:</strong> o item em foco recebe um contorno azul de
          3&nbsp;px, para você saber onde está (critério 2.4.7).
        </li>
        <li>
          <strong>Link "Pular para o conteúdo":</strong> aparece ao pressionar
          <kbd>Tab</kbd> na primeira vez e leva direto ao conteúdo, sem repassar o menu
          inteiro (critério 2.4.1).
        </li>
        <li>
          <strong>Estrutura semântica:</strong> as páginas usam regiões de navegação,
          conteúdo principal e títulos em hierarquia, o que permite ao leitor de tela pular
          de seção em seção (critério 1.3.1).
        </li>
        <li>
          <strong>Avisos anunciados em voz:</strong> mensagens de erro, sucesso e a troca de
          tela são comunicadas por regiões dinâmicas, sem precisar procurar na página
          (critério 4.1.3).
        </li>
        <li>
          <strong>Rótulos em todos os campos:</strong> cada campo tem etiqueta própria, e os
          erros são associados ao campo correspondente (critérios 3.3.1 e 3.3.2).
        </li>
        <li>
          <strong>Erro nunca indicado só pela cor:</strong> vem sempre com texto explicativo
          e destaque na borda (critério 1.4.1).
        </li>
        <li>
          <strong>Contraste adequado:</strong> texto e fundo respeitam a proporção mínima de
          4,5:1 (critério 1.4.3).
        </li>
        <li>
          <strong>Zoom até 200%:</strong> o layout se reorganiza sem perder conteúdo nem
          exigir rolagem horizontal (critério 1.4.4).
        </li>
        <li>
          <strong>Menos movimento:</strong> se o seu sistema estiver configurado para reduzir
          animações, a plataforma respeita a preferência (critério 2.3.3).
        </li>
        <li>
          <strong>Idioma declarado:</strong> as páginas identificam o português do Brasil,
          para que o leitor de tela use a pronúncia certa (critério 3.1.1).
        </li>
        <li>
          <strong>Ícones decorativos ocultos:</strong> emojis usados como enfeite são
          ignorados pelos leitores de tela, evitando leitura repetitiva.
        </li>
      </ul>
    </section>

    <section aria-labelledby="atalhos">
      <h2 id="atalhos">Atalhos de teclado</h2>
      <table class="tabela">
        <caption class="apenas-leitor-de-tela">Teclas e suas ações na plataforma</caption>
        <thead>
          <tr>
            <th scope="col">Tecla</th>
            <th scope="col">O que faz</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="atalho in atalhos" :key="atalho.tecla">
            <td><kbd>{{ atalho.tecla }}</kbd></td>
            <td>{{ atalho.acao }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section aria-labelledby="leitores">
      <h2 id="leitores">Leitores de tela</h2>
      <p>A interface foi construída seguindo os padrões usados por:</p>
      <ul>
        <li><strong>NVDA</strong> (Windows, gratuito)</li>
        <li><strong>JAWS</strong> (Windows)</li>
        <li><strong>VoiceOver</strong> (macOS e iOS)</li>
        <li><strong>TalkBack</strong> (Android)</li>
      </ul>
    </section>

    <section aria-labelledby="limitacoes">
      <h2 id="limitacoes">Limitações conhecidas</h2>
      <p>
        Prezamos pela transparência, então registramos o que ainda não está resolvido:
      </p>
      <ul>
        <li>
          <strong>PDFs enviados por usuários.</strong> A acessibilidade do conteúdo depende
          de como cada arquivo foi produzido. Um PDF digitalizado (imagem de página) não
          pode ser lido por leitores de tela nem pelo assistente de IA. Ao publicar
          material, prefira PDFs com texto selecionável.
        </li>
        <li>
          <strong>Visualização de PDF na tela de detalhes.</strong> Ela usa o leitor do
          próprio navegador, cujo comportamento varia. O botão <em>Baixar</em> é sempre uma
          alternativa para abrir o arquivo no seu leitor preferido.
        </li>
        <li>
          <strong>Validação automatizada.</strong> As verificações foram feitas manualmente
          e com base nos critérios WCAG; ainda não há auditoria por ferramenta automatizada
          em toda a aplicação.
        </li>
      </ul>
    </section>

    <section aria-labelledby="contato">
      <h2 id="contato">Encontrou uma barreira?</h2>
      <p>
        Se alguma parte da plataforma impedir o seu uso, avise a coordenação da instituição
        que mantém esta instalação. Descreva a página, o que tentou fazer e qual tecnologia
        assistiva estava usando — isso acelera muito a correção.
      </p>
    </section>

    <footer class="rodape">
      <RouterLink :to="{ name: 'privacidade' }" class="botao botao-secundario">
        Política de Privacidade
      </RouterLink>
    </footer>
  </article>
</template>

<style scoped>
.pagina {
  max-width: 820px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

section {
  margin-top: 2rem;
}

h2 {
  border-bottom: 1px solid var(--cor-borda);
  padding-bottom: 0.4rem;
}

ul {
  padding-left: 1.2rem;
}

li {
  margin-bottom: 0.5rem;
}

kbd {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--cor-borda);
  border-bottom-width: 2px;
  border-radius: 4px;
  background: var(--cor-fundo);
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.rodape {
  margin-top: 2.5rem;
}
</style>
