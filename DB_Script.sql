/****** Object:  User [hectord.godoy@urosario.edu.co]    Script Date: 14/03/2025 10:01:04 a. m. ******/
CREATE USER [hectord.godoy@urosario.edu.co] FROM  EXTERNAL PROVIDER  WITH DEFAULT_SCHEMA=[dbo]
GO
/****** Object:  User [juanse.barrios@urosario.edu.co]    Script Date: 14/03/2025 10:01:04 a. m. ******/
CREATE USER [juanse.barrios@urosario.edu.co] FROM  EXTERNAL PROVIDER  WITH DEFAULT_SCHEMA=[dbo]
GO
/****** Object:  DatabaseRole [AdminBISQLAZ]    Script Date: 14/03/2025 10:01:04 a. m. ******/
CREATE ROLE [AdminBISQLAZ]
GO
sys.sp_addrolemember @rolename = N'AdminBISQLAZ', @membername = N'hectord.godoy@urosario.edu.co'
GO
sys.sp_addrolemember @rolename = N'db_owner', @membername = N'hectord.godoy@urosario.edu.co'
GO
sys.sp_addrolemember @rolename = N'AdminBISQLAZ', @membername = N'juanse.barrios@urosario.edu.co'
GO
/****** Object:  Table [dbo].[CamposObligatorios]    Script Date: 14/03/2025 10:01:04 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CamposObligatorios](
	[id] [int] NOT NULL,
	[requerido] [varchar](50) NULL,
	[estado] [int] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[estadoValidacion]    Script Date: 14/03/2025 10:01:04 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[estadoValidacion](
	[idEstado] [int] IDENTITY(1,1) NOT NULL,
	[nombreEstado] [varchar](50) NULL,
	[fechaEstado] [varchar](50) NULL,
 CONSTRAINT [PK_estadoValidacion] PRIMARY KEY CLUSTERED 
(
	[idEstado] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PlantillasValidacion]    Script Date: 14/03/2025 10:01:04 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PlantillasValidacion](
	[idPlantillasValidacion] [int] IDENTITY(1,1) NOT NULL,
	[NombrePlantilla] [varchar](200) NOT NULL,
	[ContenidoJSON] [nvarchar](max) NOT NULL,
	[RutaJSON] [varchar](500) NULL,
	[FechaCarga] [datetime2](7) NOT NULL,
	[FechaUltimaModificacion] [datetime2](7) NULL,
	[UsuarioCargue] [varchar](200) NOT NULL,
	[EstadoPlantilla] [varchar](50) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[idPlantillasValidacion] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ProcesosAdministrativos]    Script Date: 14/03/2025 10:01:04 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ProcesosAdministrativos](
	[idProcesoAdmin] [int] IDENTITY(1,1) NOT NULL,
	[nombreProcesoAdmin] [varchar](50) NULL,
	[estadoProcesoAdmin] [varchar](50) NULL,
	[responsableProcesoAdmin] [varchar](50) NULL,
	[fechaCreacionProcesoAdmin] [date] NULL,
 CONSTRAINT [PK_ProcesosAdministrativos] PRIMARY KEY CLUSTERED 
(
	[idProcesoAdmin] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[usuariosValidador]    Script Date: 14/03/2025 10:01:04 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[usuariosValidador](
	[idUsuario] [int] IDENTITY(1,1) NOT NULL,
	[nombreUsuario] [varchar](50) NULL,
	[correoUsuario] [varchar](50) NULL,
	[estadoUsuario] [varchar](50) NULL,
	[fechaCreacionUsuario] [date] NULL,
	[datosContactoUsuario] [varchar](150) NULL,
 CONSTRAINT [PK_usuariosValidador] PRIMARY KEY CLUSTERED 
(
	[idUsuario] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Validaciones]    Script Date: 14/03/2025 10:01:04 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Validaciones](
	[idValidaciones] [int] IDENTITY(1,1) NOT NULL,
	[idProcesoAdmin] [int] NULL,
	[idUsuario] [int] NULL,
	[FechaValidacion] [date] NULL,
	[idEstado] [int] NULL,
	[idPlantillasValidacion] [int] NULL,
	[nombreArchivo] [nchar](10) NULL
) ON [PRIMARY]
GO
INSERT [dbo].[CamposObligatorios] ([id], [requerido], [estado]) VALUES (1, N'obligatorio', 1)
INSERT [dbo].[CamposObligatorios] ([id], [requerido], [estado]) VALUES (2, N'opcional', 1)
GO
SET IDENTITY_INSERT [dbo].[estadoValidacion] ON 

INSERT [dbo].[estadoValidacion] ([idEstado], [nombreEstado], [fechaEstado]) VALUES (1, N'Activo', N'12-03-2025')
INSERT [dbo].[estadoValidacion] ([idEstado], [nombreEstado], [fechaEstado]) VALUES (2, N'Inactivo', N'12-03-2025')
SET IDENTITY_INSERT [dbo].[estadoValidacion] OFF
GO
SET IDENTITY_INSERT [dbo].[PlantillasValidacion] ON 

INSERT [dbo].[PlantillasValidacion] ([idPlantillasValidacion], [NombrePlantilla], [ContenidoJSON], [RutaJSON], [FechaCarga], [FechaUltimaModificacion], [UsuarioCargue], [EstadoPlantilla]) VALUES (3, N'convertor.json', N'{
    "hojas": {
        "Hoja1": {
            "Emisor": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Grupo Económico": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Sector": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Calificacion del emisor": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Intermediario": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Titulo": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Nemotécnico": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "ISIN": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Calificación Emisión": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Operación": { "tipo": "integer", "required": true, "error_message": "Error Numerico" },
            "Tipo de Garantia": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Fecha.Compra": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Mod/Per": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Tasa de Valoración": { "tipo": "integer", "required": true, "error_message": "Error Numerico" },
            "Tasa de negociación": { "tipo": "integer", "required": true, "error_message": "Error Numerico" },
            "F. Precio Mdo": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Precio de mercado": { "tipo": "number", "maxlength": 50, "required": true, "error_message": "Error de texto" },
            "Moneda de posición": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Unidades": { "tipo": "number", "maxlength": 50, "required": true, "error_message": "Error de texto" },
            "Valor nominal":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Valor de compra":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Valor contable en moneda de posición":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Valor contable en moneda de valoración":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Fecha Reporte": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Segmento":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Nombre Portafolio": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Corredor": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "IND": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Clase de Producto": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "CVG": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Depósito": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Àrea de Valoración":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Precio Mdo promedio":{ "tipo": "number", "maxlength": 50, "required": true, "error_message": "Error de texto" },
            "Base": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Clase de contrato": {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Clase Operación":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Cod Cl Prod": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Código Intermediario": {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Interlocutor con el que hay un compromis":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "lot_id": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Modalidad Inversión":  {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Moneda valoración": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Plaza Bursatil": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Portafolio": {"tipo": "integer","required": true,"error_message": "Error Numerico"},
            "Rol Interlocutor": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Sociedad": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Tipo de cambio": { "tipo": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÁÉÍÓÚÑa-záéíóúñ0-9\\s.,@#\\$%&*()_+\\-=\\[\\]{};'':\"\\\\|,.<>\\/?]*$", "error_message": "Error de texto" },
            "Valor compra en mon.valoración": { "tipo": "integer", "required": true, "error_message": "Error Numerico" }
        }
    }
}
', N'uploads\convertor.json', CAST(N'2025-03-07T08:02:45.1918570' AS DateTime2), CAST(N'2025-03-07T08:02:45.1918620' AS DateTime2), N'hectord.godoy@urosario.edu.co', N'Activo')
INSERT [dbo].[PlantillasValidacion] ([idPlantillasValidacion], [NombrePlantilla], [ContenidoJSON], [RutaJSON], [FechaCarga], [FechaUltimaModificacion], [UsuarioCargue], [EstadoPlantilla]) VALUES (4, N'proyecto.json', N'{
    "hojas": {
        "Clientes": {
            "nombre": {
                "tipo": "string",
                "maxlength": 50,
                "required": true,
                "regex": "^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*$",
                "error_message": "El nombre debe empezar con mayúscula y contener solo letras"
            },
            "cedula": {
                "tipo": "integer",
                "min": 1000000000,
                "max": 9999999999,
                "required": true,
                "error_message": "El número de cédula debe ser un número entre 1000000000 y 9999999999"
            },
            "email": {
                "tipo": "string",
                "regex": "[^@]+@[^@]+\\.[^@]+",
                "required": true,
                "error_message": "El email debe tener un formato válido"
            }
        },
        "Pedidos": {
            "producto": {
                "tipo": "string",
                "required": true,
                "error_message": "Se requiere un producto"
            },
            "cantidad": {
                "tipo": "integer",
                "min": 1,
                "required": true,
                "error_message": "La cantidad debe ser en números"
            }
        }
    }
}', N'uploads\proyecto.json', CAST(N'2025-03-07T10:28:02.3994040' AS DateTime2), CAST(N'2025-03-07T10:28:02.3994110' AS DateTime2), N'hectord.godoy@urosario.edu.co', N'Activo')
INSERT [dbo].[PlantillasValidacion] ([idPlantillasValidacion], [NombrePlantilla], [ContenidoJSON], [RutaJSON], [FechaCarga], [FechaUltimaModificacion], [UsuarioCargue], [EstadoPlantilla]) VALUES (5, N'plantilla_Mascotas.json', N'{
    "hojas": {
        "Perros": {
            "nombre": {"type": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÃ�Ã‰Ã�Ã“ÃšÃ‘][a-zÃ¡Ã©Ã­Ã³ÃºÃ±]*$" , "error_message": "El nombre debe empezar con mayuscula y contener solo letras"},
            "tamaño": {"type": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÃ�Ã‰Ã�Ã“ÃšÃ‘][a-zÃ¡Ã©Ã­Ã³ÃºÃ±]*$" , "error_message": "El Tamaño debe empezar con mayuscula y contener solo letras"},
            "edad": {"type": "integer", "min": 1000000000,"max": 9999999999,"required": true, "error_message": "El numero de cedula debe tener 10 digitos"}
        },
        "Gatos": {
            "nombre": {"type": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÃ�Ã‰Ã�Ã“ÃšÃ‘][a-zÃ¡Ã©Ã­Ã³ÃºÃ±]*$" , "error_message": "El nombre debe empezar con mayuscula y contener solo letras"},
            "tamaño": {"type": "string", "maxlength": 50, "required": true, "regex": "^[A-ZÃ�Ã‰Ã�Ã“ÃšÃ‘][a-zÃ¡Ã©Ã­Ã³ÃºÃ±]*$" , "error_message": "El Tamaño debe empezar con mayuscula y contener solo letras"},
            "edad": {"type": "integer", "min": 1000000000,"max": 9999999999,"required": true, "error_message": "El numero de cedula debe tener 10 digitos"}
        }   
    }
}', N'uploads\plantilla_Mascotas.json', CAST(N'2025-03-07T10:54:31.4991890' AS DateTime2), CAST(N'2025-03-07T10:54:31.4991950' AS DateTime2), N'hectord.godoy@urosario.edu.co', N'Activo')
INSERT [dbo].[PlantillasValidacion] ([idPlantillasValidacion], [NombrePlantilla], [ContenidoJSON], [RutaJSON], [FechaCarga], [FechaUltimaModificacion], [UsuarioCargue], [EstadoPlantilla]) VALUES (6, N'proyecto.json', N'{
    "hojas": {
        "Clientes": {
            "nombre": {
                "tipo": "string",
                "maxlength": 50,
                "required": true,
                "regex": "^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*$",
                "error_message": "El nombre debe empezar con mayúscula y contener solo letras"
            },
            "cedula": {
                "tipo": "integer",
                "min": 1000000000,
                "max": 9999999999,
                "required": true,
                "error_message": "El número de cédula debe ser un número entre 1000000000 y 9999999999"
            },
            "email": {
                "tipo": "string",
                "regex": "[^@]+@[^@]+\\.[^@]+",
                "required": true,
                "error_message": "El email debe tener un formato válido"
            }
        },
        "Pedidos": {
            "producto": {
                "tipo": "string",
                "required": true,
                "error_message": "Se requiere un producto"
            },
            "cantidad": {
                "tipo": "integer",
                "min": 1,
                "required": true,
                "error_message": "La cantidad debe ser en números"
            }
        }
    }
}', N'uploads\proyecto.json', CAST(N'2025-03-07T13:26:49.2842780' AS DateTime2), CAST(N'2025-03-07T13:26:49.2842820' AS DateTime2), N'hectord.godoy@urosario.edu.co', N'Activo')
INSERT [dbo].[PlantillasValidacion] ([idPlantillasValidacion], [NombrePlantilla], [ContenidoJSON], [RutaJSON], [FechaCarga], [FechaUltimaModificacion], [UsuarioCargue], [EstadoPlantilla]) VALUES (7, N'proyecto.json', N'{
    "hojas": {
        "Clientes": {
            "nombre": {
                "tipo": "string",
                "maxlength": 50,
                "required": true,
                "regex": "^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*$",
                "error_message": "El nombre debe empezar con mayúscula y contener solo letras"
            },
            "cedula": {
                "tipo": "integer",
                "min": 1000000000,
                "max": 9999999999,
                "required": true,
                "error_message": "El número de cédula debe ser un número entre 1000000000 y 9999999999"
            },
            "email": {
                "tipo": "string",
                "regex": "[^@]+@[^@]+\\.[^@]+",
                "required": true,
                "error_message": "El email debe tener un formato válido"
            }
        },
        "Pedidos": {
            "producto": {
                "tipo": "string",
                "required": true,
                "error_message": "Se requiere un producto"
            },
            "cantidad": {
                "tipo": "integer",
                "min": 1,
                "required": true,
                "error_message": "La cantidad debe ser en números"
            }
        }
    }
}', N'uploads\proyecto.json', CAST(N'2025-03-14T09:43:01.8036940' AS DateTime2), CAST(N'2025-03-14T09:43:01.8037140' AS DateTime2), N'hectord.godoy@urosario.edu.co', N'Activo')
SET IDENTITY_INSERT [dbo].[PlantillasValidacion] OFF
GO
SET IDENTITY_INSERT [dbo].[ProcesosAdministrativos] ON 

INSERT [dbo].[ProcesosAdministrativos] ([idProcesoAdmin], [nombreProcesoAdmin], [estadoProcesoAdmin], [responsableProcesoAdmin], [fechaCreacionProcesoAdmin]) VALUES (1, N'Recursos humanos', N'Activo', N'juanse.barrios@urosario.edu.co', CAST(N'2025-03-12' AS Date))
INSERT [dbo].[ProcesosAdministrativos] ([idProcesoAdmin], [nombreProcesoAdmin], [estadoProcesoAdmin], [responsableProcesoAdmin], [fechaCreacionProcesoAdmin]) VALUES (2, N'direccion Tecnologica', N'Inactivo', N'hectord.godoy@urosario.edu.co', CAST(N'2025-03-12' AS Date))
SET IDENTITY_INSERT [dbo].[ProcesosAdministrativos] OFF
GO
SET IDENTITY_INSERT [dbo].[usuariosValidador] ON 

INSERT [dbo].[usuariosValidador] ([idUsuario], [nombreUsuario], [correoUsuario], [estadoUsuario], [fechaCreacionUsuario], [datosContactoUsuario]) VALUES (1, N'juan sebastian barrios', N'juanse.barrios@urosario.edu.co', N'Activo', CAST(N'2025-03-12' AS Date), N'1234567890')
INSERT [dbo].[usuariosValidador] ([idUsuario], [nombreUsuario], [correoUsuario], [estadoUsuario], [fechaCreacionUsuario], [datosContactoUsuario]) VALUES (2, N'Hector Deibyd Godoy Cardenas', N'hectord.godoy@urosario.edu.co', N'Activo', CAST(N'2025-03-12' AS Date), N'3246239115')
SET IDENTITY_INSERT [dbo].[usuariosValidador] OFF
GO
SET IDENTITY_INSERT [dbo].[Validaciones] ON 

INSERT [dbo].[Validaciones] ([idValidaciones], [idProcesoAdmin], [idUsuario], [FechaValidacion], [idEstado], [idPlantillasValidacion], [nombreArchivo]) VALUES (5, 1, 1, CAST(N'2025-03-12' AS Date), 1, 4, N'Libro1.xls')
INSERT [dbo].[Validaciones] ([idValidaciones], [idProcesoAdmin], [idUsuario], [FechaValidacion], [idEstado], [idPlantillasValidacion], [nombreArchivo]) VALUES (6, 1, 1, CAST(N'2025-03-12' AS Date), 1, 4, N'Libro1.xls')
INSERT [dbo].[Validaciones] ([idValidaciones], [idProcesoAdmin], [idUsuario], [FechaValidacion], [idEstado], [idPlantillasValidacion], [nombreArchivo]) VALUES (7, 1, 1, CAST(N'2025-03-13' AS Date), 1, 4, N'Libro1.xls')
INSERT [dbo].[Validaciones] ([idValidaciones], [idProcesoAdmin], [idUsuario], [FechaValidacion], [idEstado], [idPlantillasValidacion], [nombreArchivo]) VALUES (9, 1, 1, CAST(N'2025-03-13' AS Date), 1, 4, N'Libro1.xls')
INSERT [dbo].[Validaciones] ([idValidaciones], [idProcesoAdmin], [idUsuario], [FechaValidacion], [idEstado], [idPlantillasValidacion], [nombreArchivo]) VALUES (10, 2, 1, CAST(N'2025-03-13' AS Date), 1, 4, N'Libro1.xls')
INSERT [dbo].[Validaciones] ([idValidaciones], [idProcesoAdmin], [idUsuario], [FechaValidacion], [idEstado], [idPlantillasValidacion], [nombreArchivo]) VALUES (11, 1, 1, CAST(N'2025-03-14' AS Date), 1, 4, N'Libro1.xls')
SET IDENTITY_INSERT [dbo].[Validaciones] OFF
GO
ALTER TABLE [dbo].[PlantillasValidacion] ADD  CONSTRAINT [DF_PlantillasValidacion_FechaCarga]  DEFAULT (sysdatetime()) FOR [FechaCarga]
GO
ALTER TABLE [dbo].[Validaciones]  WITH CHECK ADD  CONSTRAINT [FK_Validaciones_EstadoValidacion] FOREIGN KEY([idEstado])
REFERENCES [dbo].[estadoValidacion] ([idEstado])
GO
ALTER TABLE [dbo].[Validaciones] CHECK CONSTRAINT [FK_Validaciones_EstadoValidacion]
GO
ALTER TABLE [dbo].[Validaciones]  WITH CHECK ADD  CONSTRAINT [FK_Validaciones_ProcesosAdministrativos] FOREIGN KEY([idProcesoAdmin])
REFERENCES [dbo].[ProcesosAdministrativos] ([idProcesoAdmin])
GO
ALTER TABLE [dbo].[Validaciones] CHECK CONSTRAINT [FK_Validaciones_ProcesosAdministrativos]
GO
ALTER TABLE [dbo].[Validaciones]  WITH CHECK ADD  CONSTRAINT [FK_Validaciones_Usuarios] FOREIGN KEY([idUsuario])
REFERENCES [dbo].[usuariosValidador] ([idUsuario])
GO
ALTER TABLE [dbo].[Validaciones] CHECK CONSTRAINT [FK_Validaciones_Usuarios]
GO
