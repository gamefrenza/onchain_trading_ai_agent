import React, { useState, useEffect } from 'react';
import { formatDistance } from 'date-fns';
import { TradeActivity } from '../types';

interface TradeActivityFeedProps {
    websocket: WebSocket;
}

export const TradeActivityFeed: React.FC<TradeActivityFeedProps> = ({ websocket }) => {
    const [activities, setActivities] = useState<TradeActivity[]>([]);
    
    useEffect(() => {
        websocket.onmessage = (event) => {
            const trade = JSON.parse(event.data);
            setActivities(prev => [trade, ...prev].slice(0, 50));  // Keep last 50 trades
        };
    }, [websocket]);
    
    return (
        <div className="trade-activity-feed">
            <h3>Recent Trading Activity</h3>
            <div className="activity-list">
                {activities.map((activity) => (
                    <div key={activity.id} className="activity-item">
                        <div className={`activity-type ${activity.type}`}>
                            {activity.type.toUpperCase()}
                        </div>
                        <div className="activity-details">
                            <span className="pair">{activity.pair}</span>
                            <span className="amount">{activity.amount}</span>
                            <span className="price">${activity.price}</span>
                        </div>
                        <div className="activity-time">
                            {formatDistance(new Date(activity.timestamp), new Date(), { addSuffix: true })}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}; 