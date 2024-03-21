Уважаемый студент !

Спасибо за качественно выполненную домашнюю работу !

Работа выполнена качественно, мне понравились комментарии, код читается легко.

1. В первом задании добвил код, который поможет проанализировать структуру базы.
2. Во втором задании можно улучшить код, следуя принципу [DRY](https://ru.wikipedia.org/wiki/Don%E2%80%99t_repeat_yourself)
и стараться следовать [принципам](https://12factor.net/ru/).
3. Чтобы было удобнее запускать Elasticsearch, прилагаю файл docker-compose.yml 
## Инструкция

Контейнер полностью готов к запуску. 

Сначала нужно склонировать репозиторий

```shell
git clone https://github.com/Anycharacters/praktikum.git
cd praktikum
```


Для запуска нужен Docker.
Как узнать установлен ли Docker ?


| Команда            |Если установлен|Если не установлен| Как устновить                                     |
|--------------------|---|---|---------------------------------------------------|
| ```docker -v``` |Docker version хх.хх.хх, build ххххх|bash: docker: command not found| [ссылка](https://docs.docker.com/engine/install/) |
|```docker compose version```|Docker Compose version vx.xx.x|bash: docker: command not found|[ссылка](https://docs.docker.com/compose/install/)|

После установки Docker-a нужно из текущей директории запустить контейнер командой

```shell
docker compose up --build
```


