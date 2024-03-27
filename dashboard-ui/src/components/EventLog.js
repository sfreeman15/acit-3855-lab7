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
                <div style="display: flex; justify-content: center;">
                    <table>
                        <tbody>
                            <tr>
                                <td># Event 0001 Logged: {stats["0001"]}</td>
                            </tr>
                            <tr>
                                <td># Event 0002 Logged: {stats["0002"]}</td>
                            </tr>
                            <tr>
                                <td># Event 0003 Logged: {stats["0003"]}</td>
                            </tr>
                            <tr>
                                <td># Event 0004 Logged: {stats["0004"]}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

        );
    }
}
