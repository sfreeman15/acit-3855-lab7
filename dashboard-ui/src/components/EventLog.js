import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppEvents() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getEvents = () => {
	
        fetch(`http://acit-3855-kafka.westus3.cloudapp.azure.com:8120/event_stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received events")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getEvents(), 4000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getEvents]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Event Log</h1>
                <table className={"EventTable"}>
					<tbody>
						<tr>
							<td># Event 0001: {stats['0001']}</td>
							<td># Event 0002 {stats['0002']}</td>
                            <td># Event 0002 {stats['0003']}</td>
                            <td># Event 0004 {stats['0004']}</td>
						</tr>
					</tbody>
                </table>

            </div>
        )
    }
}
