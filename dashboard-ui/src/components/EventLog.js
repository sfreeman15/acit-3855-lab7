import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
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
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Ticket Purchase</th>
							<th>Ticket Upload</th>
						</tr>
						<tr>
							<td># Ticket Purchase: {stats['num_tp_readings']}</td>
							<td># Ticket Upload: {stats['num_tu_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Amount of Ticket Purchase Requests: {stats['max_tp_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Amount of Ticket Upload {stats['max_tu_readings']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
