[TOC]

### 1. Postgre setting with Django

```bash
$ pip install psycopg2-binary 
```

```bash
$ brew install postgresql@10 # 12버전 error
```

1. **Create a new user in Postgres**

   ```bash
   $ psql postgres
   ```

   ```sql
   postgres=# CREATE USER [sample_user] WITH PASSWORD 'sample_password';
   ```

   or

   ```sql
   postgres=# CREATE USER sample_user;
   ```

2. **Create a new database and give the new user access**

   ```sql
   postgres=# CREATE DATABASE [sample_database] WITH OWNER sample_user;
   ```

3. **List of roles**

   ```sql
   postgres=# \du
   ```

   ```sql
                                      List of roles
    Role name |                         Attributes                         | Member of 
   -----------+------------------------------------------------------------+-----------
    harryjjun |                                                            | {}
    postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
   ```

4. **Make a role**

   ```sql
   postgres=# ALTER ROLE harryjjun CREATEDB;
   ```

   ```sql
   postgres=# \du
   ```

   ```sql
                                      List of roles
    Role name |                         Attributes                         | Member of 
   -----------+------------------------------------------------------------+-----------
    harryjjun | Create DB                                                  | {}
    postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
   ```

   ```sql
   postgres=# \q
   ```

5. **login with user**

   ```bash
   $ psql [DB_NAME] -U [USER_NAME]
   ```

6. **List of databases**

   ```SQL
   DB_NAME=> \l
   ```

   ```sql
      Name    |   Owner   | Encoding |   Collate   |    Ctype    |   Access privileges   
   -----------+-----------+----------+-------------+-------------+-----------------------
    hpweek    | harryjjun | UTF8     | en_US.UTF-8 | en_US.UTF-8 | 
    template0 | postgres  | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/junhokim          +
              |           |          |             |             | junhokim=CTc/junhokim
   ```



- settings.py

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'django_test',
          'USER': 'root',
          'PASSWORD': '',
          'HOST': 'localhost',
          'PORT': '',
      }
  }
  ```



---



### 2. Install architect

- 라이브러리 설치 후 모델에 다음과 같이 작성

  ```bash
  $ pip install architect
  ```

  ```python
  from django.db import models
  import architect
  
  # Create your models here.
  class Board(models.Model):
      pass
  
      def __str__(self):
          return str(self.pk)
  
  
  @architect.install('partition', type='range', subtype='integer', constraint='2', column='board_id')
  class Article(models.Model):
      title = models.CharField(max_length=30)
      content = models.TextField()
      board = models.ForeignKey(Board, on_delete=models.CASCADE)
  
      def __str__(self):
          return self.title
  ```

  - `board_id` 를 기준(2개)으로 article 의 파티션을 나누도록 설정





---



### 3. Migration and Partition

```bash
$ python manage.py makemigrations
```

```bash
$ python manage.py migrate
```

```bash
$ export DJANGO_SETTINGS_MODULE=[project_name].settings
```

```bash
$ architect partition --module [app_name].models

architect partition: result: successfully (re)configured the database for the following models: Article
```



```bash
$ python manage.py dbshell
```

로 실행하면

```bash
$ psql [DB_NAME] -U [USER_NAME]
```

로 실행한 것과 동일



---



### 4. DB TEST

> admin 페이지 혹은 django shell 에서 데이터 넣기 진행



- 보드 1에 글 3개 작성 후 테이블 확인

  ```
  hpweek=# \dt
  ```

  ```sql
                      List of relations
   Schema |            Name            | Type  |   Owner   
  --------+----------------------------+-------+-----------
   public | articles_article           | table | harryjjun
   public | articles_article_1_2       | table | harryjjun
   public | articles_board             | table | harryjjun
  ...
  ```

  ```sql
  hpweek=# SELECT * FROM articles_article;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    1 | 1 board 의 1번 글 | 내용    |        1
    2 | 1 board 의 2번 글 | 내용    |        1
    3 | 1 board 의 3번 글 | 내용    |        1
  (3 rows)
  ```

  ```sql
  hpweek=# SELECT * FROM articles_article_1_2;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    1 | 1 board 의 1번 글 | 내용    |        1
    2 | 1 board 의 2번 글 | 내용    |        1
    3 | 1 board 의 3번 글 | 내용    |        1
  (3 rows)
  ```

  - `articles_article_1_2` 테이블에는 board_id 가 1,2 인 article 만 작성된다.



- 보드 2에 글 1개 작성

  ```sql
  hpweek=# SELECT * FROM articles_article;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    1 | 1 board 의 1번 글 | 내용    |        1
    2 | 1 board 의 2번 글 | 내용    |        1
    3 | 1 board 의 3번 글 | 내용    |        1
    4 | 2 board 의 1번 글 | 내용    |        2
  (4 rows)
  ```

  ```sql
  hpweek=# SELECT * FROM articles_article_1_2;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    1 | 1 board 의 1번 글 | 내용    |        1
    2 | 1 board 의 2번 글 | 내용    |        1
    3 | 1 board 의 3번 글 | 내용    |        1
    4 | 2 board 의 1번 글 | 내용    |        2
  (4 rows)
  ```

  

- 보드 3에 글 2개 작성

  ```sql
                      List of relations
   Schema |            Name            | Type  |   Owner   
  --------+----------------------------+-------+-----------
   public | articles_article           | table | harryjjun
   public | articles_article_1_2       | table | harryjjun
   public | articles_article_3_4       | table | harryjjun
   public | articles_board             | table | harryjjun
  ...
  ```

  ```sql
  hpweek=# SELECT * FROM articles_article;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    1 | 1 board 의 1번 글 | 내용    |        1
    2 | 1 board 의 2번 글 | 내용    |        1
    3 | 1 board 의 3번 글 | 내용    |        1
    4 | 2 board 의 1번 글 | 내용    |        2
    5 | 3 board 의 1번 글 | 내용    |        3
    6 | 3 board 의 2번 글 | 내용    |        3
  ```

  ```SQL
  hpweek=# SELECT * FROM articles_article_1_2;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    1 | 1 board 의 1번 글 | 내용    |        1
    2 | 1 board 의 2번 글 | 내용    |        1
    3 | 1 board 의 3번 글 | 내용    |        1
    4 | 2 board 의 1번 글 | 내용    |        2
  ```

  ```SQL
  hpweek=# SELECT * FROM articles_article_3_4;
   id |       title       | content | board_id 
  ----+-------------------+---------+----------
    5 | 3 board 의 1번 글 | 내용    |        3
    6 | 3 board 의 2번 글 | 내용    |        3
  ```

  - 역시나 `board_id` 기준으로 2개씩 분할되어 파티션되어 저장되고 있음. (e.g. 1과2, 3과4 ...)



- shell_plus

  ```python
  >>> Article.objects.filter(Q(board_id=1)|Q(board_id=3))
  
  <QuerySet [<Article: 1 board 의 1번 글>, <Article: 1 board 의 2번 글>, <Article: 1 board 의 3번 글>, <Article: 3 board 의 1번 글>, <Article: 3 board 의 2번 글>]>
  ```



---



### [참고] Architect Tools

- 사용법

  ```python
  import architect
  
  @architect.install(feature, **options)
  class Model(object):
      pass
  ```

**options**

- `type` (required) - Partition type (e.g. `range`, `list`)
- `subtype` (required) - Partition subtype ( `date`, `integer`, `##`)
- `constraint` (required) - What data fits into partition (`day`, `5`, ...)
- `column` (required). Column, which value determines which partition record belongs to (`day`, `5`, ...)



**Partitioning Performance (Postgres)**

> https://www.qwertee.io/blog/postgres-data-partitioning-and-django/

파티셔닝은 특정 기준에 따라 데이터를 나누므로 파티션 내부의 순차적 스캔을 통해 단일 파티션의 큰 덩어리에 액세스 할 때 쿼리가 더 빠르게 실행됨.

INSERT 가 빨라진다. 테이블을 작은 테이블로 나눈다는 것은 다시 계산할 인덱스가 작다는 것을 의미. 조건부 선택 및 조인은 적은 데이터에서 작동하기 때문에 더 빠르게 실행. 

파티션이 조건을 충족하지 않음을 감지하면 쿼리를 실행할 때 해당 파티션을 사용하지 않는다. 파티셔닝이 수행되는 기준은 성능 개선에 중요.



---



> 참고문헌
>
> https://docs.djangoproject.com/en/2.2/ref/databases/#postgresql-notes
>
> https://docs.djangoproject.com/en/2.2/ref/settings/#databases
>
> http://www.postgresqltutorial.com/
>
> https://architect.readthedocs.io/features/partition/postgresql.html#postgresql
>
> https://medium.com/agatha-codes/painless-postgresql-django-d4f03364989
>
> https://goonan.io/setting-up-postgresql-on-os-x-2/
>
> https://stackoverflow.com/questions/1137060/where-does-postgresql-store-the-database