document.addEventListener('DOMContentLoaded', () => {
    const columnDefs = [
        {colId: 'cuenta.codigo', field: 'cuenta.codigo', rowGroup: true, hide: true},
        {colId: 'cuenta.nombre', field: 'cuenta.nombre', rowGroup: true, hide: true},
        {headerName: 'Cuenta Codigo', showRowGroup: 'cuenta.codigo', cellRenderer: 'agGroupCellRenderer',},
        {headerName: 'Cuenta Nombre', showRowGroup: 'cuenta.nombre', cellRenderer: 'agGroupCellRenderer',},
        {headerName: 'Debe', field: 'debe',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Haber', field: 'haber',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Debe', field: 'debe',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Haber', field: 'haber',
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            aggFunc: 'sum'
        },
        {headerName: 'Total Debe',
            valueGetter: params => {
                const debe = parseFloat(params.node.aggData?.debe || 0);
                const haber = parseFloat(params.node.aggData?.haber || 0);
                return debe > haber ? (debe - haber).toFixed(2) : "0.00";
            },
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            cellClass: 'total-cell',
        },
        {headerName: 'Total Haber',
            valueGetter: params => {
                const debe = parseFloat(params.node.aggData?.debe || 0);
                const haber = parseFloat(params.node.aggData?.haber || 0);
                return haber > debe ? (haber - debe).toFixed(2) : "0.00";
            },
            valueFormatter: params => parseFloat(params.value || 0).toFixed(2),
            cellClass: 'total-cell',
        }
    ];

    const gridOptions = {
        columnDefs: columnDefs,
        // groupDisplayType: 'groupRows',
        groupDisplayType: 'custom',
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
        },
        autoGroupColumnDef: {
            headerName: 'Grupo',
            cellRendererParams: {
                suppressCount: true,
                innerRenderer: params => {
                    // Validar si el nodo actual es una agrupación
                    if (params.node.group) {
                        const codigo = params.node.key || ''; // Clave del grupo (código)
                        const nombre = params.node.aggData ? params.node.aggData['cuenta.nombre'] || '' : ''; // Nombre del grupo
                        return `<strong>${codigo}</strong> - ${nombre}`;
                    } else {
                        // Fallback para nodos sin agrupación
                        return params.value || '';
                    }
                }
            },
        },
        groupIncludeFooter: true,
        animateRows: true,
        suppressAggFuncInHeader: true,
    };

    const eGridDiv = document.querySelector('#myGrid');
    new agGrid.Grid(eGridDiv, gridOptions);

    // Función para cargar los datos
    const loadData = async () => {
        try {
            const response = await fetch( window.location.pathname, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'action': 'searchdata',
                }),
            });

            const rawData = await response.json();

            if (rawData.error) {
                console.error('Error al cargar los datos:', rawData.error);
                return;
            }

            // Procesar datos: asegurarse de que los valores sean numéricos
            const processedData = rawData.map(item => ({
                ...item,
                debe: parseFloat(item.debe || 0),
                haber: parseFloat(item.haber || 0),
            }));

            // Establece los datos en la grid
            gridOptions.api.setRowData(processedData);
        } catch (error) {
            console.error('Error realizando la petición AJAX:', error);
        }
    };

    // Llama a la función para cargar los datos
    loadData();

    document.getElementById('exportExcel').addEventListener('click', () => {
        const rowData = [];
        gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
            const data = node.group
                ? {
                      Grupo: node.key,
                      TotalDebe: node.aggData.debe.toFixed(2),
                      TotalHaber: node.aggData.haber.toFixed(2),
                  }
                : {
                      CuentaCodigo: node.data['cuenta.codigo'],
                      CuentaNombre: node.data['cuenta.nombre'],
                      Debe: node.data.debe.toFixed(2),
                      Haber: node.data.haber.toFixed(2),
                  };
            rowData.push(data);
        });

        const worksheet = XLSX.utils.json_to_sheet(rowData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Datos');
        XLSX.writeFile(workbook, 'export.xlsx');
    });

    document.getElementById('exportPdf').addEventListener('click', () => {
        const doc = new jspdf.jsPDF();
        const groupedData = [];

        gridOptions.api.forEachNodeAfterFilterAndSort((node) => {
            if (node.group) {
                groupedData.push([`Grupo: ${node.key}`, '', '', '', `Debe: ${node.aggData.debe.toFixed(2)}`, `Haber: ${node.aggData.haber.toFixed(2)}`]);
            } else {
                groupedData.push([
                    node.data['cuenta.codigo'],
                    node.data['cuenta.nombre'],
                    node.data.debe.toFixed(2),
                    node.data.haber.toFixed(2),
                    '',
                    ''
                ]);
            }
        });

        doc.text('Exportación a PDF', 10, 10);

        doc.autoTable({
            head: [['Cuenta Código', 'Cuenta Nombre', 'Debe', 'Haber', 'Total Debe', 'Total Haber']],
            body: groupedData,
            startY: 20
        });

        // Guarda el PDF
        doc.save('balance.pdf');
    });

});

