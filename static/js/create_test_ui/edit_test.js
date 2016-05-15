var CreateTest = require('./modules.js');
var Cases = CreateTest.Cases;
var ReactDOM = require('react-dom');


var get_cases = function(self){
    $.getJSON('')
        .success(function (data) {
            var cases = (data["cases"] || []).map(function (item, index) {
                return <CreateTest.Case
                    key={index}
                    case_id={index}
                    top_data_handler={self.data_handler}
                    delete_case={self.delete_case}
                    isnew={false}
                    tests={item.tests}
                    expects={item.expects}
                    db_id ={item.id}
                />
            });
            self.setState({
                cases: cases,
                description: data["description"] || ''
            });
        })
        .error(function (data) {
            console.log("err", data);
        });
};

ReactDOM.render(<Cases init_funcs={[get_cases]}/>, document.getElementById('main_container'));
