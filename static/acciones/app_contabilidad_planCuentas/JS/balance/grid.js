/*const gridOptions = {
  columnDefs: [
    { field: 'country', rowGroup: true, hide: true },
    { field: 'year', rowGroup: true, hide: true },
    { field: 'athlete' },
    { field: 'sport' },
    { field: 'gold' },
    { field: 'silver' },
    { field: 'bronze' },
  ],
  defaultColDef: {
    flex: 1,
    minWidth: 100,
    sortable: true,
    resizable: true,
  },
  autoGroupColumnDef: {
    minWidth: 200,
  },
  groupDisplayType: 'multipleColumns',
  animateRows: true,
};

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
  var gridDiv = document.querySelector('#myGrid');
  new agGrid.Grid(gridDiv, gridOptions);

  fetch('https://www.ag-grid.com/example-assets/olympic-winners.json')
    .then((response) => response.json())
    .then((data) => gridOptions.api.setRowData(data));
});*/


let dtos = [];
let obterner = () => {
  $.ajax({
    url: window.location.pathname,
    type: 'POST',
    data: {
      'action': 'searchdata'
    },
    dataType: 'json',

  }).done(function (data) {
    console.log('data del grid')
    console.log(data)

    data.map(function (x) {
        dtos.push({
          codigo_cuenta_plan: x.codigo_cuenta_plan,
          nombre_cuenta_plan: x.nombre_cuenta_plan,
          debe: x.debe,
          haber: x.haber
      })
    })

      const gridOptions = {
      columnDefs: [
        {
          field: 'codigo_cuenta_plan',
          rowGroup: true,
          sortable: true,
          sort: 'asc',
        },
        {
          field: 'nombre_cuenta_plan',
          rowGroup: true,
          sortable: true,
          sort: 'asc',
        },
        {field: 'debe'},
        {field: 'haber'}
      ],
      defaultColDef: {
        flex: 1,
        minWidth: 100,
        filter: true,
        sortable: true,
        resizable: true,
      },
      autoGroupColumnDef: {
        minWidth: 300,
      },
      groupDefaultExpanded: 1,
      rowData: data,
    };

// setup the grid after the page has finished loading
    document.addEventListener('DOMContentLoaded', function () {
      var gridDiv = document.querySelector('#myGrid');
      new agGrid.Grid(gridDiv, gridOptions);
    });

  });
}




obterner();