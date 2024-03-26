import React, { useEffect, useState } from 'react';
import '../App.css';

export default function AppEvents() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null);

    const getEvents = () => {
        fetch(`http://acit-3855-kafka.westus3.cloudapp.azure.com:8120/event_stats`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log("Received events", result);
                    setStats(result);
                    setIsLoaded(true);
                },
                (error) => {
                    setError(error);
                    setIsLoaded(true);
                }
            );
    };

    useEffect(() => {
        const interval = setInterval(getEvents, 4000); // Update every 4 seconds
        return () => clearInterval(interval);
    }, []);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>);
    } else if (!isLoaded) {
        return (<div>Loading...</div>);
    } else {
        return (
            <div>
                <table className={"EventTable"}>
                    <tbody>
                        <tr>
                            <tr><td># Event 0001: {stats["0001"]}</td></tr>
                            <tr>  <td># Event 0002: {stats["0002"]}</td></tr>
                            <tr> <td># Event 0003: {stats["0003"]}</td></tr>
                            <tr> <td># Event 0004: {stats["0004"]}</td></tr>
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}
