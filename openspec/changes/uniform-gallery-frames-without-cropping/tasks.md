## 1. Frame uniforme

- [x] 1.1 Restaurar o formato externo quadrado em todos os cards; verificar que retrato, paisagem e quadrado usam a mesma proporção de frame.
- [x] 1.2 Configurar as imagens internas com `object-fit: fill` para ocupar todo o card, sem `object-fit: cover`; verificar que não existe corte.
- [x] 1.3 Manter o grid responsivo com no máximo três colunas em mobile, tablet e desktop; verificar as regras CSS em cada breakpoint.

## 2. Interação

- [x] 2.1 Manter a ação de apagar sobre o card com `aria-label`, contraste e foco visível; verificar a ação em imagens retrato, paisagem e quadradas.
- [x] 2.2 Verificar que upload, exclusão, loading, estado vazio, toast e invalidação de cache continuam funcionando após o frame uniforme.

## 3. Verificação

- [x] 3.1 Atualizar a verificação automatizada para exigir frame quadrado, `object-fit: fill` e ausência de `object-fit: cover`; verificar o cenário com três proporções.
- [ ] 3.2 Executar lint, typecheck e build do frontend; verificar que a aplicação compila sem regressões.
