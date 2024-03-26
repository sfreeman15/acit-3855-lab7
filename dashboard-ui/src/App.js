import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'
import AppEvents from "./components/EventLog"

function App() {

    const endpoints = ["sales/purchase", "sales/upload"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="150px" width="400px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <h1> Event Logs </h1>
                <AppEvents/>
            </div>
        </div>
    );

}



export default App;
