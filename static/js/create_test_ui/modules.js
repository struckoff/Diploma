module.exports = (function (vars) {
    var m = function() {
        React = require('react');
        var Modal = require('react-modal');
        const ModalStyle = {
            content: {
                top: '50%',
                left: '50%',
                right: 'auto',
                bottom: 'auto',
                marginRight: '-50%',
                transform: 'translate(-50%, -50%)'
            }
        };

        var Case = React.createClass({
            getInitialState: function () {
                return {
                    tests_field: this.field_build({id: 'tests', handler: this.tests_handl}),
                    expects_field: this.field_build({id: 'expects', handler: this.expects_handl}),
                    temp: {
                        tests: '',
                        expects: ''
                    },
                    tests: this.props.tests || '',
                    expects: this.props.expects || '',
                    db_id: this.props.db_id || -1,
                    modalIsOpen: false,
                    isnew: typeof(this.props.isnew) == "boolean" ? this.props.isnew : true,
                    save_button: <button onClick={this.save_case} className="btn btn-success">Save</button>
                }
            },
            openModal: function () {
                this.setState({
                    tests_field: this.field_build({
                        id: 'tests',
                        handler: this.tests_handl,
                        value: this.state.tests
                    }),
                    expects_field: this.field_build({
                        id: 'expects',
                        handler: this.expects_handl,
                        value: this.state.expects
                    }),
                    temp: {
                        tests: this.state.tests,
                        expects: this.state.expects
                    }
                });
                this.setState({modalIsOpen: true});
            },
            closeModal: function () {
                this.setState({modalIsOpen: false});
            },
            field_build: function (data) {
                var self = this;
                var handler = function (e) {
                    self.state.temp[data.id] = e.target.value;
                    self.setState(self.state);
                };

                return <textarea
                    className="form-control"
                    type="text"
                    id={data.id}
                    defaultValue={data.value}
                    onChange={handler}>
                </textarea>
            },
            save_case: function () {
                this.setState({
                    tests: this.state.temp.tests,
                    expects: this.state.temp.expects,
                    isnew: false
                });
                data = {
                    "tests" : this.state.temp.tests,
                    "expects": this.state.temp.expects,
                    "id": this.state.db_id
                };
                if (this.props.top_data_handler) {
                    this.props.top_data_handler(this.props.case_id, data);
                }
                this.closeModal();
            },
            cancel: function () {
                this.setState({
                    temp: {
                        db_id: -1,
                        tests: '',
                        expects: ''
                    }
                });
                this.closeModal();
                if (this.state.isnew) {
                    this.delete_case();
                }
            },
            delete_case: function (e) {
                this.props.delete_case(this.props.case_id);
            },
            render: function () {
                return (
                    <div className="col-sm-12">
                        <div className="col-sm-5">
                            <div id="tests" className='well well-sm form-control'>
                                {this.state.tests}
                            </div>
                        </div>
                        <div className="col-sm-5">
                            <div id="expects" className='well well-sm form-control'>
                                {this.state.expects}
                            </div>
                        </div>
                        <div className="btn-group">
                            <button onClick={this.openModal} className="btn btn-default">Edit</button>
                            <button onClick={this.delete_case} className="btn btn-danger">X</button>
                        </div>
                        <Modal
                            className="Modal__Bootstrap modal-dialog"
                            isOpen={this.state.modalIsOpen||this.state.isnew}
                            onRequestClose={this.closeModal}
                            style={ModalStyle}
                        >
                            <div className="col-sm-12">
                                <div className="col-sm-6">
                                    {this.state.tests_field}
                                </div>
                                <div className="col-sm-6">
                                    {this.state.expects_field}
                                </div>
                            </div>
                            <div className="col-sm-12">
                                <div className="col-sm-6">
                                    <button onClick={this.save_case} className="btn btn-success">Save</button>
                                </div>
                                <div className="col-sm-6">
                                    <button className="btn" onClick={this.cancel}>Cancel</button>
                                </div>
                            </div>
                        </Modal>
                    </div>
                );
            }

        });

        var Cases = React.createClass({
            getInitialState: function () {
                return {
                    cases: [],
                    case_id: 0,
                    description: ''
                }
            },
            componentDidMount: function(){
                var self = this;
                (this.props.init_funcs || []).map(function(f){
                    f(self);
                })
            },
            data: {},
            state_check: function () {
                return this.state;
            },
            data_handler: function (case_id, data) {
                this.data = this.data || {};
                this.data[case_id.toString()] = this.data[case_id.toString()] || {};
                for (key in data) {
                    this.data[case_id.toString()][key] = data[key];
                }
            },
            description_handler: function (e) {
                this.setState({
                    description: e.target.value || this.state.description
                })
            },
            new_case: function () {
                this.setState({
                    cases: this.state.cases.concat([
                        <Case
                            key={this.state.cases.length}
                            case_id={this.state.cases.length}
                            top_data_handler={this.data_handler}
                            delete_case={this.delete_case}
                        />
                    ])
                });
            },
            send_cases: function (e) {
                $.getJSON('', {
                        cases: JSON.stringify(this.data),
                        description: this.state.description
                    })
                    .success(function (data) {
                        if (window.location.pathname != data.url){
                            window.open(data.url, '_self')
                        }
                    })
                    .error(function (data) {
                        console.log('err', data);
                    })
            },
            delete_case: function (case_id) {
                delete this.state.cases[case_id];
                delete this.data[case_id];
                this.setState(this.state);
            },
            render: function () {
                return (
                    <div>
                        <div id="description" className="left_col col-md-5 left">
                            <div className="btn btn-lg btn-block"></div>
                            <textarea onChange={this.description_handler} rows="10" placeholder="Description" value={this.state.description}></textarea>
                        </div>
                        <div className="right_col col-md-7 right">
                            <div id="buttons">
                                <button id="new_case" className="btn btn-primary col-md-3" onClick={this.new_case}>New case</button>
                                <button id="send_cases" className="btn btn-primary col-md-3" onClick={this.send_cases}>Save</button>
                            </div>
                            <div id="cases">
                                {this.state.cases}
                            </div>
                        </div>
                    </div>
                )
            }
        });
        this.Case = Case;
        this.Cases = Cases;
    };
    return new m;
})();