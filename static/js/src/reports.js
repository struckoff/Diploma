var React = require('react');
var ReactDOM = require('react-dom');
var $ = jQuery = require('jquery');

var Codemirror = require('react-codemirror');
require('codemirror/mode/javascript/javascript');

var App = React.createClass({
    getInitialState: function () {
        return {
            reports: [],
            report_body: null,
            items_raw: [],
            active_item: -1
        };
    },
    get_body: function (item) {
        var self = this;

        $.getJSON(window.location.href + '/get', {report_id: item.id})
            .success(function (data) {
                self.setState({report_body: <ReportBody data={data} key={data.id}/>});
            }).error(function (e, err) {
            console.log(e, err);
        });
        this.setState({active_item: item.id});
        this.componentDidMount();

    },
    get_list_item: function (item) {
        var state = (item.id == this.state.active_item) ? "list-group-item-success" : "";
        return (
            <div onClick={this.get_body.bind(null, item)}
                 className={"list_item list-group-item "  + state}>
                <h3 className="list-group-item-heading">{item.name}</h3>
            </div>
        )
    },
    componentDidMount: function () {
        var reports = [];
        var self = this;
        $.getJSON(window.location.href + '/get')
            .success(function (data) {
                (data || []).map(function (item) {
                    reports[item.id] = self.get_list_item(item)
                });
                self.setState({
                    reports: reports,
                    items_raw: data
                });
            })
            .error(function (e, err) {
                this.state.items_raw.map(function (item) {
                    reports[item.id] = self.get_list_item(item)
                });
                self.setState({reports: reports});
                console.log(e, err);
            });
    },
    render: function () {
        return (
            <div className="row">
                <div className="items_list col-md-3 list-group">
                    {this.state.reports}
                </div>
                <div id="output" className="col-md-6">
                    {this.state.report_body}
                </div>
            </div>
        )
    }
});


var ReportBody = React.createClass({
    getInitialState: function () {
        return {};
    },
    get_cases: function () {
        var cases = [];
        (this.props.data.passed || []).map(function (item) {
            cases[item.id] = (<div className="row alert alert-success" style={{"padding-bottom":0}}>
                <div className="col-xs-6">
                    <div className="well well-sm form-control">{item.tests}</div>
                </div>
                <div className="col-xs-6">
                    <div className="well well-sm form-control">{item.expects}</div>
                </div>
            </div>)
        });
        (this.props.data.failed || []).map(function (item) {
            cases[item.id] = (<div className="row alert alert-danger" style={{"padding-bottom":0}}>
                <div className="col-xs-6">
                    <div className="well well-sm form-control">{item.tests}</div>
                </div>
                <div className="col-xs-6">
                    <div className="well well-sm form-control">{item.expects}</div>
                </div>
            </div>)
        });
        return cases;
    },
    render: function () {
        var data = this.props.data;
        var options = {
            lineNumbers: true,
            theme: this.state.theme || 'dracula',
            readOnly: true,
            mode: 'javascript'
        };
        return (
            <div className="list_item well">
                <Codemirror ref='output' value={data.code || ''} options={options}/>
                <div className="form-horizontal well well-sm">
                    <div className="form-group">
                        <label for="name" className="col-lg-2 control-label">Name</label>
                        <div className="col-lg-10">
                            <span id="name" className="form-control">{data.name || ""}</span>
                        </div>
                    </div>
                    <div className="form-group">
                        <label for="name" className="col-lg-2 control-label">Comment</label>
                        <div className="col-lg-10">
                            <span id="about" className="form-control">{data.about || ""}</span>
                        </div>
                    </div>
                </div>
                <div className="cases_legend row alert bg-primary">
                    <label className="col-xs-6">Test params</label>
                    <label className="col-xs-6">Expects</label>
                </div>
                {this.get_cases()}
            </div>
        )
    }
});

ReactDOM.render(
    <App />
    , document.getElementById('reports'));