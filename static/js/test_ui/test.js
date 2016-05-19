var React = require('react');
var ReactDOM = require('react-dom');
var $ = require('jquery');
require("../bootstrap/js/bootstrap.min.js");

var Codemirror = require('react-codemirror');
require('codemirror/mode/javascript/javascript');



var App = React.createClass({
    getInitialState: function() {
        return {
            code: 'function (a, b) {return a + b}',
            theme: 'default'
        };
    },
    updateCode: function(newCode) {
        this.setState({
            code: newCode
        });
    },
    submit: function(e){
        var data_send = {
            text: this.state.code
        };
        $.getJSON('', data_send)
            .success(function(data){
                ReactDOM.render(<Output data={data} />, document.getElementById('output'));
            }).error(function(e, err){
            console.log(e, err);
        });
    },
    switchTheme: function(e){
        this.setState({
            theme: e.target.value,
        });
    },
    render: function() {
        var options = {
            lineNumbers: true,
            theme: this.state.theme,
            mode:  'javascript'
        };
        return (
            <div>
                <Codemirror ref='editor' value={this.state.code} onChange={this.updateCode} options={options} />
                <nav className="navbar navbar-inverse navbar-default">
                    <div className="navbar-form navbar-left">
                        <button className="btn btn-primary" type='button' onClick={this.submit}>
                            Submit
                        </button>
                    </div>
                    <div className="themeswitch navbar-form navbar-right">
                        <select onChange={this.switchTheme} value={this.state.theme} className="form-control cont">
                            <option value="default">default</option>
                            <option value="monokai">monokai</option>
                            <option value="zenburn">zenburn</option>
                            <option value="solarized dark">solarized dark</option>
                            <option value="solarized light">solarized light</option>
                            <option value="twilight">twilight</option>
                        </select>
                    </div>
                </nav>
            </div>
        )
    }
});

var Output = React.createClass({
    render: function(){
        console.log(this.props);
        return (
            <div>
                <div id="statistic" className="col-md-5 col-md-push-7">
                    <div className={"panel panel-" + this.props.data.statistic.style}>
                        <div className="panel-heading">
                            <h3 className="panel-title">Quick review</h3>
                        </div>
                        <div className="panel-body">
                            <div id="ratio">{this.props.data.statistic.ratio + '% '}</div>
                        </div>
                    </div>
                </div>
                <div id="test_results_cont" className="col-md-7 col-md-pull-5">
                    <table id="test_results" className="table table-responsive">
                        <thead>
                        <tr>
                            <th>#</th>
                            <th>State</th>
                            <th>Message</th>
                        </tr>
                        </thead>
                        <tbody>
                        {
                            this.props.data.results.map(function (result, result_index){
                                return (
                                    <tr key={"result_" + result_index} className={"result" + result.state?"pass success":"not_pass danger"}>
                                        <td>{result_index}</td>
                                        <td className="state">{result.state?"Pass":"Fail"}</td>
                                        <td className="message">{result.message}</td>
                                    </tr>
                                )
                            })
                        }
                        </tbody>
                    </table>
                </div>
            </div>
        )
    }
});

ReactDOM.render(<App />, document.getElementById('editor'));


$('#form').on('submit',function(e) {
    e.preventDefault();
    })
