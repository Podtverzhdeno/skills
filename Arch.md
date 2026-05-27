# JAVA / KOTLIN PROJECT HEURISTICS

`gigacode.md` — главный источник по конкретному проекту:
- модули
- слои
- структура пакетов
- связи между компонентами

Но кроме `gigacode.md`, агент ОБЯЗАН использовать типовую карту Java/Kotlin-проектов, чтобы быстро находить нужные файлы без полного обхода репозитория.

---

# ОБЩИЙ ПОРЯДОК ПОИСКА

1. Прочитать `gigacode.md`
2. Определить framework и стиль архитектуры
3. Определить ожидаемые package names
4. Искать файлы только в вероятных слоях
5. Не обходить весь проект без необходимости

---

# ГДЕ ОБЫЧНО ЧТО ЛЕЖИТ

## API layer
Искать в:
- `controller/`
- `controllers/`
- `resource/`
- `resources/`
- `route/`
- `routes/`
- `api/`
- `rest/`
- `grpc/`
- `handler/`
- `endpoint/`

Обычно содержит:
- REST endpoints
- gRPC handlers
- GraphQL resolvers
- WebSocket handlers

## Service layer
Искать в:
- `service/`
- `services/`
- `usecase/`
- `usecases/`
- `application/`
- `business/`
- `domain/service/`

Обычно содержит:
- бизнес-логику
- orchestration
- use-cases
- transaction logic

## Persistence layer
Искать в:
- `repository/`
- `repositories/`
- `dao/`
- `persistence/`
- `database/`
- `db/`
- `storage/`

Обычно содержит:
- CRUD
- SQL/ORM access
- запросы к БД

## Domain / models
Искать в:
- `entity/`
- `entities/`
- `domain/`
- `model/`
- `models/`
- `aggregate/`

Обычно содержит:
- entity classes
- domain objects
- enums
- aggregates

## DTO / contracts
Искать в:
- `dto/`
- `request/`
- `response/`
- `contract/`
- `contracts/`
- `payload/`
- `transport/`

Обычно содержит:
- request/response models
- API contracts

## Mapper layer
Искать в:
- `mapper/`
- `mappers/`
- `converter/`
- `transformer/`
- `adapter/`

Обычно содержит:
- DTO ↔ Entity mapping
- Domain ↔ DTO mapping

## Security layer
Искать в:
- `security/`
- `auth/`
- `authentication/`
- `authorization/`
- `jwt/`
- `oauth/`

Обычно содержит:
- JWT
- OAuth2
- auth filters
- access control

## Validation layer
Искать в:
- `validation/`
- `validator/`
- `constraints/`

Обычно содержит:
- request validation
- custom validators

## Exception layer
Искать в:
- `exception/`
- `exceptions/`
- `error/`
- `errors/`
- `handler/`
- `advice/`

Обычно содержит:
- custom exceptions
- global exception handlers
- error response models

## Client / integration layer
Искать в:
- `client/`
- `clients/`
- `integration/`
- `integrations/`
- `external/`
- `gateway/`
- `connector/`
- `adapter/`

Обычно содержит:
- external API clients
- Feign/WebClient/RestTemplate wrappers
- third-party integrations

## Event / messaging
Искать в:
- `event/`
- `events/`
- `kafka/`
- `messaging/`
- `consumer/`
- `producer/`
- `listener/`
- `rabbitmq/`

Обычно содержит:
- consumers
- producers
- listeners
- event handlers

## Scheduler
Искать в:
- `scheduler/`
- `job/`
- `jobs/`
- `cron/`
- `task/`
- `tasks/`

Обычно содержит:
- `@Scheduled` jobs
- periodic tasks
- cleanup jobs

## Config / infrastructure
Искать в:
- `config/`
- `configuration/`
- `filter/`
- `interceptor/`
- `aspect/`
- `middleware/`

Обычно содержит:
- framework config
- bean config
- logging/tracing/audit
- request interception

---

# ТИПОВЫЕ ПРИЗНАКИ ПО FRAMEWORK

## Spring Boot
Искать:
- `@RestController`
- `@RequestMapping`
- `@Service`
- `@Repository`
- `@Configuration`

## Micronaut
Искать:
- `@Controller`
- `@Singleton`
- `@Inject`

## Quarkus / JAX-RS
Искать:
- `@Path`
- `@ApplicationScoped`
- `@GET`
- `@POST`

## Ktor
Искать:
- `routing { }`
- `get { }`
- `post { }`
- `Application.module`

## gRPC
Искать:
- `*.proto`
- `XxxGrpc`
- `ImplBase`
- `bindService`

---

# ПРАВИЛО ПОИСКА

Если нужно найти реализацию API:
1. сначала искать в API layer
2. затем в service layer
3. затем в repository/client
4. только после этого смотреть вспомогательные слои

Если `gigacode.md` уже описывает модули и пакеты, использовать его как карту проекта, а эту секцию — как универсальную схему для быстрой навигации по Java/Kotlin кодовой базе.
