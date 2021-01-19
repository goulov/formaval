# formaval
Sistema para distribuição de versões para provas de avaliação.

Desenvolvido para a disciplina de CP e EP do IST em 2020/21.

---

## para instalar (requer nginx)
- `$ pip install -r requirements.txt`
- exportar do fénix as folhas de cálculo com as listas de alunos (`Gerar Folha De Cálculo`) das disciplinas e converter para `.csv` (manter o nome original, ex: `CP325179577_-_Alunos.csv`)
- definir os parâmetros em `parameters.py`
    - definir `paths2csv` com os nomes dos csv numa lista
    - definir `dbpath` com o nome da base de dados para o teste
    - definir `N` com o número de testes por turno
    - definir `randomizer` com um valor aleatório para evitar que as distribuições sejam iguais em testes diferentes
    - definir `delay` com o intervalo de tempo desde o início turno até ao teste
    - definir `test_duration` com o intervalo de tempo desde o início do teste até ao fim do teste
    - definir `mapa_turnos` com a correspondência entre o código do turno e a semana, dia da semana e hora do turno
- colocar as versões dos testes em `testes/{nome_do_turno}/{versao}.pdf` (onde `{versao}` vai de `1` a `N`). Por exemplo (2 versões),
```
$ tree ./testes/
testes/
├── a1_CP325179577PB04
│   ├── 1.pdf
│   └── 2.pdf
├── a_CP325179577PB07
│   ├── 1.pdf
│   └── 2.pdf
├── a_EPro35179577PB04
│   ├── 1.pdf
│   └── 2.pdf
├── b1_CP325179577PB04
│   ├── 1.pdf
│   └── 2.pdf
├── b_CP325179577PB07
│   ├── 1.pdf
│   └── 2.pdf
└── b_EPro35179577PB04
    ├── 1.pdf
    └── 2.pdf
```
- `python createdb.py` cria a base de dados com os alunos

## para correr
- correr gunicorn em background: `./run.sh`
- configurar `nginx`:
    - `ln -s $PWD/nginx/formaval /etc/nginx/sites-available/formaval`
    - password do `/viewdb` é criada (username: `admin`) com `htpasswd -c /etc/nginx/.htpasswd admin`

## para utilizar
- o endpoint `/` recebe o IST ID e disponibiliza a versão adequada, o pedido é registado
- o endpoint `/viewdb` mostra as tabelas da base de dados
- o script cria um ficheiro com logs `./log_formaval.log`

## exemplos das páginas
![formulario](https://user-images.githubusercontent.com/50577030/105055548-18435b00-5a6b-11eb-822c-57ed4773ee5f.png)

![logs](https://user-images.githubusercontent.com/50577030/105055556-1a0d1e80-5a6b-11eb-8ddf-bbb37f41b141.png)
