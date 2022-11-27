db.detallesPedidos.aggregate(
    [
        {
            $match: {
                "codDetalle": "PE22112-1"
            }
        },
        {
            $lookup:{
                from: "productos",
                localField: "detalleProducto.codProducto",
                foreignField: "codProducto",
                as: "producto"
            }
        },
        {
            $unwind: "$producto"
        },
        {
            $lookup:{
                from: "produccion",
                localField: "codDetalle",
                foreignField: "codDetalle",
                as: "produccion"
            }
        },
        {
            $unwind: "$produccion"
        },
        {
            $project:{
                codProduccion: "$produccion.CodDetalle",
                producto: "$producto.descripcion",
                cantidadRestante: "$produccion.cantidadRestante",
                cantidad: "$cantidad",
                descripcion: "$descripcion",
                fechaEntrega: "$fechaEntrega",
                etapa:{
                    codEtapa: "$produccion.etapa.codEtapa",
                    descripcion: "$produccion.etapa.descripcion"
                }
            }
        }
    ]
)

db.usuarios.aggregate(
    [
        {
            $match:{
                "_id": ObjectId("6354940ea18bed59e3211e05")
            }
        },
        {
            $lookup:{
                from: "tiposUsuarios",
                localField: "codTipoUsuario",
                foreignField: "codTipo",
                as: "tipoUsuario"
            }
        }
    ]

)
