function MessageBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`bubble ${isUser ? "user" : "assistant"}`}>
      <div className="bubble-role">{isUser ? "You" : "Assistant"}</div>
      <div className="bubble-text">{message.content}</div>
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="sources">
          <span>Sources:</span>
          <ul>
            {message.sources.map((s, idx) => (
              <li key={idx}>
                {s.source} (score {s.score?.toFixed(2)})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default MessageBubble;

