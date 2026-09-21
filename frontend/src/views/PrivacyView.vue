<script setup>
import { RouterLink } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// A versão precisa acompanhar TERMS_VERSION em backend/apps/accounts/models.py.
const versao = '1.0'
const atualizadoEm = 'setembro de 2026'
</script>

<template>
  <article class="pagina">
    <header>
      <h1>Política de Privacidade e Termos de Uso</h1>
      <p class="texto-suave">
        Versão {{ versao }} · atualizada em {{ atualizadoEm }}
      </p>
    </header>

    <section aria-labelledby="resumo">
      <h2 id="resumo">Em resumo</h2>
      <ul class="resumo">
        <li>Coletamos apenas nome, e-mail e o que você mesmo envia para o acervo.</li>
        <li>Seus documentos nascem <strong>privados</strong> e só ficam públicos se você publicar.</li>
        <li>O assistente de IA roda <strong>na máquina da instituição</strong>: nenhum conteúdo é enviado a serviços externos.</li>
        <li>Você pode baixar todos os seus dados ou apagar sua conta quando quiser.</li>
        <li>Não vendemos, alugamos nem compartilhamos dados com terceiros.</li>
      </ul>
    </section>

    <section aria-labelledby="controlador">
      <h2 id="controlador">1. Quem trata os seus dados</h2>
      <p>
        A instituição de ensino que mantém esta instalação do Acervo Edu IA é a
        <strong>controladora</strong> dos dados pessoais, nos termos do art. 5º, VI, da
        Lei 13.709/2018 (LGPD). Dúvidas e pedidos relativos aos seus dados devem ser
        encaminhados ao encarregado de dados indicado pela instituição.
      </p>
    </section>

    <section aria-labelledby="dados">
      <h2 id="dados">2. Quais dados são tratados</h2>
      <table class="tabela">
        <caption class="apenas-leitor-de-tela">
          Dados coletados, finalidade e base legal
        </caption>
        <thead>
          <tr>
            <th scope="col">Dado</th>
            <th scope="col">Para que serve</th>
            <th scope="col">Base legal</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Nome</td>
            <td>Identificar você na plataforma e creditar a autoria dos documentos</td>
            <td>Consentimento (art. 7º, I)</td>
          </tr>
          <tr>
            <td>E-mail</td>
            <td>Login e identificação da conta</td>
            <td>Consentimento (art. 7º, I)</td>
          </tr>
          <tr>
            <td>Senha</td>
            <td>Proteger o acesso — guardada apenas como hash, nunca em texto legível</td>
            <td>Segurança (art. 46)</td>
          </tr>
          <tr>
            <td>Perfil e instituição</td>
            <td>Definir o que cada pessoa pode fazer no sistema</td>
            <td>Legítimo interesse (art. 7º, IX)</td>
          </tr>
          <tr>
            <td>Documentos enviados</td>
            <td>Guardar, organizar e — se você publicar — compartilhar o material</td>
            <td>Consentimento (art. 7º, I)</td>
          </tr>
          <tr>
            <td>Perguntas ao assistente</td>
            <td>Montar o seu histórico de consultas, visível apenas para você</td>
            <td>Consentimento (art. 7º, I)</td>
          </tr>
          <tr>
            <td>Data e versão do aceite</td>
            <td>Comprovar o consentimento, como exige o art. 8º, § 1º</td>
            <td>Cumprimento legal (art. 7º, II)</td>
          </tr>
        </tbody>
      </table>
      <p class="texto-suave">
        Não coletamos CPF, telefone, endereço, localização nem dados sensíveis (art. 5º, II).
        Não usamos cookies de rastreamento nem ferramentas de publicidade.
      </p>
    </section>

    <section aria-labelledby="ia">
      <h2 id="ia">3. Como funciona o assistente de IA</h2>
      <p>
        O assistente usa um modelo de linguagem executado <strong>localmente</strong>, por
        meio do Ollama, na própria máquina que hospeda o sistema. Quando você faz uma
        pergunta:
      </p>
      <ol>
        <li>o sistema confere se você tem permissão para acessar aquele documento;</li>
        <li>extrai o texto do arquivo e envia, junto com sua pergunta, ao modelo local;</li>
        <li>devolve a resposta na tela e a guarda no seu histórico.</li>
      </ol>
      <p>
        <strong>Nenhum conteúdo sai da máquina da instituição.</strong> Não há chamada a
        serviços de IA na nuvem, nem envio de dados a terceiros para treinar modelos. Um
        arquivo enviado apenas para uma pergunta avulsa é lido na memória e descartado logo
        depois — ele não entra no acervo.
      </p>
      <p>
        A IA apenas responde: ela nunca altera, publica ou apaga documentos, e nenhuma
        decisão automatizada é tomada sobre você com base nas respostas dela.
      </p>
    </section>

    <section aria-labelledby="compartilhamento">
      <h2 id="compartilhamento">4. Quem pode ver o quê</h2>
      <ul>
        <li>
          <strong>Documentos privados:</strong> apenas você e, para fins de moderação,
          os perfis Gestor e Administrador.
        </li>
        <li>
          <strong>Documentos publicados:</strong> todos os usuários cadastrados na
          plataforma. Ao publicar, o sistema pede uma confirmação explícita.
        </li>
        <li>
          <strong>Histórico do assistente:</strong> somente você.
        </li>
        <li>
          <strong>Nome e e-mail:</strong> visíveis ao Administrador, que gerencia as contas.
          Seu nome aparece como autor nos documentos que você publicar.
        </li>
      </ul>
    </section>

    <section aria-labelledby="seguranca">
      <h2 id="seguranca">5. Segurança</h2>
      <ul>
        <li>Senhas guardadas com hash e validadores de força (art. 46 da LGPD).</li>
        <li>
          Arquivos nunca ficam em endereço público: todo download passa por uma verificação
          de permissão no servidor, e o arquivo é gravado em disco com nome aleatório.
        </li>
        <li>Sessões autenticadas por token com prazo de validade.</li>
        <li>Permissões conferidas sempre no servidor, nunca apenas escondendo botões.</li>
      </ul>
    </section>

    <section aria-labelledby="retencao">
      <h2 id="retencao">6. Por quanto tempo guardamos</h2>
      <p>
        Seus dados ficam guardados enquanto a conta existir. Ao excluir a conta, o sistema
        apaga em definitivo o cadastro, os documentos enviados (inclusive os arquivos em
        disco) e todo o histórico de perguntas ao assistente. A exclusão é imediata e não
        pode ser desfeita.
      </p>
    </section>

    <section aria-labelledby="direitos">
      <h2 id="direitos">7. Seus direitos (art. 18 da LGPD)</h2>
      <table class="tabela">
        <caption class="apenas-leitor-de-tela">Direitos do titular e onde exercê-los</caption>
        <thead>
          <tr>
            <th scope="col">Direito</th>
            <th scope="col">Onde exercer</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Confirmar e acessar os dados</td>
            <td>Meu Perfil → <em>Baixar meus dados</em></td>
          </tr>
          <tr>
            <td>Portabilidade</td>
            <td>Meu Perfil → <em>Baixar meus dados</em> (arquivo JSON)</td>
          </tr>
          <tr>
            <td>Corrigir dados incompletos ou desatualizados</td>
            <td>Meu Perfil → editar nome; documentos → Editar</td>
          </tr>
          <tr>
            <td>Eliminar os dados e revogar o consentimento</td>
            <td>Meu Perfil → <em>Excluir minha conta</em></td>
          </tr>
          <tr>
            <td>Informação sobre compartilhamento</td>
            <td>Seção 4 desta política — não há compartilhamento com terceiros</td>
          </tr>
          <tr>
            <td>Reclamar à ANPD</td>
            <td>
              <a href="https://www.gov.br/anpd" target="_blank" rel="noopener noreferrer">
                gov.br/anpd
                <span class="apenas-leitor-de-tela">(abre em nova aba)</span>
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section aria-labelledby="uso">
      <h2 id="uso">8. Termos de uso</h2>
      <p>Ao usar a plataforma, você se compromete a:</p>
      <ul>
        <li>
          enviar apenas material de sua autoria ou que você tenha direito de compartilhar,
          respeitando a Lei 9.610/1998 (direitos autorais);
        </li>
        <li>não publicar conteúdo ofensivo, ilegal ou com dados pessoais de terceiros;</li>
        <li>não tentar acessar documentos ou contas de outras pessoas;</li>
        <li>manter sua senha em segredo.</li>
      </ul>
      <p>
        Documentos que violem estas regras podem ser despublicados ou removidos pelos
        perfis Gestor e Administrador.
      </p>
    </section>

    <section aria-labelledby="mudancas">
      <h2 id="mudancas">9. Mudanças nesta política</h2>
      <p>
        Se o texto mudar de forma relevante, a versão é atualizada e o sistema pede um novo
        aceite no próximo acesso. O consentimento anterior fica registrado com a data e a
        versão a que se referia.
      </p>
    </section>

    <footer class="rodape">
      <RouterLink v-if="auth.autenticado" :to="{ name: 'perfil' }" class="botao">
        Ir para Meu Perfil
      </RouterLink>
      <RouterLink v-else :to="{ name: 'entrar' }" class="botao botao-secundario">
        Voltar para o login
      </RouterLink>
      <RouterLink :to="{ name: 'acessibilidade' }" class="botao botao-secundario">
        Declaração de Acessibilidade
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

ul,
ol {
  padding-left: 1.2rem;
}

li {
  margin-bottom: 0.4rem;
}

.resumo {
  background: var(--cor-primaria-clara);
  border-radius: var(--raio);
  padding: 1rem 1rem 1rem 2.2rem;
}

.tabela {
  margin-bottom: 0.75rem;
}

.rodape {
  margin-top: 2.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>
