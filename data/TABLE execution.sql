CREATE TABLE `code` (
    `id` int NOT NULL AUTO_INCREMENT,
    `code` varchar(100) DEFAULT NULL,                   /* Шифр проекта с указанием номера листа            */
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `result` (
    `id` int NOT NULL AUTO_INCREMENT,
    `result` tinyint(1) NOT NULL DEFAULT (0),           /* Результат принято, не принято, не предъявлено    */
    `note_result` varchar(255) DEFAULT NULL,            /* Примечание                                       */
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `execution` (
    `id` int NOT NULL AUTO_INCREMENT,
    `application_number` varchar(100) NULL,             /* Номер заявки в формате год-неделя-№п/п           */
    `number_estimate` varchar(100) DEFAULT NULL,        /* Номер по смете контракта при наличии             */
    `number_order` int NOT NULL,                        /* Номер по порядку в заявке                        */
    `name_id` int NOT NULL,                             /* id из таблицы name_of_works_and_materials        */
    `dimension_id` int NOT NULL,                        /* id из таблицы dimension                          */
    `value` float DEFAULT NULL,                         /* Количество работ, материалов                     */
    `code_id` int NOT NULL,                             /* id шифр проекта таблица code                     */
    `plan` tinyint(1) NOT NULL DEFAULT (1),             /* Объёмы сдавались по плану или вне плана          */
    `date_plan` date DEFAULT NULL,                      /* Дата вызова при наличии                          */
    `date_fackt` date DEFAULT NULL,                     /* Дата фактического освидетельствования            */
    `date_executive_documentation` date DEFAULT NULL,   /* Дата предоставления исполнительной документации  */
    `result_id` int NOT NULL,                           /* Результат освидетельствования таблица result     */
    `note` varchar(255) DEFAULT NULL,                   /* Примечание                                       */
    `contractor_id` int NOT NULL,                       /* id компании подрядчика таблица contractor        */
    `persone_contractor_id` int NOT NULL,               /* id представителя подрядчика таблица people       */
    `executor_id` int NOT NULL,                         /* id производителя работ таблица contractor        */
    `persone_executor_id` int NOT NULL,                 /* id представителя производ. работ - people        */
    `construction_control_id` int NOT NULL,             /* id инженера строительного контроля - people      */
    PRIMARY KEY (`id`),
    FOREIGN KEY (`name_id`) REFERENCES `name_of_works_and_materials` (`id`),
    FOREIGN KEY (`dimension_id`) REFERENCES `dimension` (`id`),
    FOREIGN KEY (`code_id`) REFERENCES `code` (`id`),
    FOREIGN KEY (`result_id`) REFERENCES `result` (`id`),
    FOREIGN KEY (`contractor_id`) REFERENCES `contractor` (`id`),
    FOREIGN KEY (`persone_contractor_id`) REFERENCES `people` (`id`),
    FOREIGN KEY (`executor_id`) REFERENCES `contractor` (`id`),
    FOREIGN KEY (`persone_executor_id`) REFERENCES `people` (`id`),
    FOREIGN KEY (`construction_control_id`) REFERENCES `people` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci