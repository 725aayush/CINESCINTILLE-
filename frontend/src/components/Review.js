import React from 'react';
import api from '../api';
import '../styles/movieDetail.css';

export default function Review({ review, currentUser, onRefresh }) {
  
  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this review?")) {
      try {
        await api.delete(`/review/${review.id}`);
        onRefresh(); // Trigger a reload in the parent component
      } catch (err) {
        alert("Failed to delete review.");
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

      {currentUser && currentUser.id === review.user_id && (
        <button onClick={handleDelete} className="comment-delete-btn">
          Delete Review
        </button>
      )}
    </div>
  );
}