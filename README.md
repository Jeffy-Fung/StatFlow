# StatFlow

## Project Overview
StatFlow is a comprehensive statistical analysis and data visualization tool designed to aid researchers and analysts in interpreting complex datasets. The project aims to provide a user-friendly interface along with powerful backend functionalities to streamline the data analysis workflow.

## Features
- **Statistical Analysis**: Perform various statistical tests and analysis techniques on your data.
- **Visualizations**: Generate interactive plots and charts to better understand your data.
- **User Management**: Secure login and user management system to keep your data safe.
- **API Access**: Access the backend via a RESTful API for seamless integration with other applications.

## Tech Stack
- **Frontend**: React.js for building interactive user interfaces.
- **Backend**: Node.js with Express.js for handling server-side logic.
- **Database**: MongoDB for data storage and retrieval.
- **Authentication**: JSON Web Tokens (JWT) for secure user authentication.
- **Testing**: Jest and Mocha for unit testing.

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Jeffy-Fung/StatFlow.git
   cd StatFlow
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Set up the database**:
   - Ensure MongoDB is installed and running.
   - Create a database for StatFlow.

4. **Run the application**:
   ```bash
   npm start
   ```
   The application should be running on http://localhost:3000.

## API Documentation
- **Get Data**: `GET /api/data`
  - Retrieves all datasets.

- **Post Data**: `POST /api/data`
  - Adds a new dataset. (Requires authentication)

- **Update Data**: `PUT /api/data/:id`
  - Updates an existing dataset. (Requires authentication)

- **Delete Data**: `DELETE /api/data/:id`
  - Deletes a specified dataset. (Requires authentication)

## File Format Requirements
- CSV files are required for data uploads.
- The first row must contain headers, and all data types should be consistent per column.

## Usage Examples
1. **Uploading a dataset**:
   - Use the `Upload` button in the UI to upload a CSV file.

2. **Generating visualizations**:
   - Select your dataset and choose visualization options from the menu.

3. **Statistical Analysis**:
   - Navigate to the `Analysis` tab to perform statistical tests on your dataset.

## Future Enhancements
- Introduce machine learning capabilities for predictive analytics.
- Enhance user experience with improved UI components.
- Add support for more file formats (e.g., Excel, JSON).
- Optimize performance for larger datasets.

---

For further information, please reach out to the [StatFlow team](mailto:support@statflow.io).