import React from 'react';
import api from '../api';

export default function ReviewCard({ review, currentUser, onRefresh }) {
  
  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this review?")) {
      try {
        await api.delete(`/review/${review.id}`);
        onRefresh(); // Refresh the list in the parent component
      } catch (err) {
        console.error("Delete failed:", err);
      }
    }
  };

  return (
    <div className="review-comment-card">
      <div className="review-header">
        <div className="user-info">
          <img 
            src={`/static/avatars/${review.avatar || 'default.jpg'}`} 
            alt={review.username} 
            className="comment-avatar"
          />
          <span className="comment-username">{review.username}</span>
        </div>
        <div className="comment-rating">
          {"★".repeat(review.rating)}{"☆".repeat(5 - review.rating)}
        </div>
      </div>
      
      <div className="comment-body">
        <p>{review.comment}</p>
      </div>

      {/* Only allow deletion if the logged-in user matches the review author */}
      {currentUser && currentUser.username === review.username && (
        <button onClick={handleDelete} className="comment-delete-link">
          Delete Review
        </button>
      )}
    </div>
  );
}