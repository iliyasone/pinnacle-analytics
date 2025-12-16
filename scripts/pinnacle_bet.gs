// ============================================
// CONFIGURATION
// ============================================
const DAYS_TO_FETCH = 1; // Number of days to look back for bets

// ============================================
// MAIN FUNCTION - Fetch and append bets
// ============================================
function fetchAndAppendBets() {
  try {
    // Get the active spreadsheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const betsSheet = ss.getSheetByName('BETS');
    
    // Validate sheet exists
    if (!betsSheet) {
      throw new Error('BETS sheet not found. Please run Setup Sheets first.');
    }
    
    // Get API configuration from Script Properties
    const scriptProperties = PropertiesService.getScriptProperties();
    const apiUrl = scriptProperties.getProperty('API_URL');
    const apiToken = scriptProperties.getProperty('API_TOKEN');
    
    if (!apiUrl || !apiToken) {
      throw new Error('API_URL or API_TOKEN not found in Script Properties. Please run "Set API Credentials" from the menu.');
    }
    
    Logger.log('Fetching account name...');
    const accountName = getAccountName(apiUrl, apiToken);
    Logger.log('Account name: ' + accountName);
    
    Logger.log('Fetching bets...');
    const bets = getBets(apiUrl, apiToken);
    Logger.log('Found ' + bets.length + ' bets');
    
    // Get existing bet IDs to avoid duplicates
    const existingBetIds = getExistingBetIds(betsSheet);
    Logger.log('Existing bet IDs in sheet: ' + existingBetIds.size);
    
    // Filter out bets that already exist
    const newBets = bets.filter(bet => !existingBetIds.has(bet.betId));
    Logger.log('New bets to add: ' + newBets.length);
    
    if (newBets.length === 0) {
      SpreadsheetApp.getUi().alert('No new bets to add.');
      return;
    }
    
    // Calculate total profit in stakes
    const totalProfit = newBets.reduce((sum, bet) => {
      let profit;
      if (bet.betStatus === 'WON') {
        profit = bet.winLoss || bet.win || 0;
      } else if (bet.betStatus === 'LOST') {
        profit = -(bet.risk || 0);
      } else {
        profit = 0;
      }
      return sum + profit;
    }, 0);
    
    // Append new bets
    appendBetsToSheet(betsSheet, newBets, accountName);
    
    // Format profit for display
    const profitSign = totalProfit >= 0 ? '+' : '';
    const profitFormatted = profitSign + totalProfit.toFixed(2);
    
    // Show success message
    const message = `${newBets.length} bet${newBets.length !== 1 ? 's were' : ' was'} imported!\n${profitFormatted} stakes profit`;
    SpreadsheetApp.getUi().alert(message);
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

// ============================================
// Get account name from API
// ============================================
function getAccountName(baseUrl, token) {
  const url = baseUrl.replace(/\/$/, '') + '/account_info';
  

  const options = {
    'method': 'get',
    'headers': {
      'x-api-key': token,
      'Content-Type': 'application/json'
    },
    'muteHttpExceptions': true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  
  if (responseCode !== 200) {
    throw new Error('Failed to fetch account info. Status: ' + responseCode + ', Response: ' + response.getContentText());
  }
  
  const data = JSON.parse(response.getContentText());
  return data.account_name || 'Unknown';
}

// ============================================
// Get bets from API
// ============================================
function getBets(baseUrl, token) {
  // Calculate date range
  const toDate = new Date();
  const fromDate = new Date();
  fromDate.setDate(fromDate.getDate() - DAYS_TO_FETCH);
  
  // Format dates as YYYY-MM-DD
  const fromDateStr = Utilities.formatDate(fromDate, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const toDateStr = Utilities.formatDate(toDate, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  
  const url = baseUrl.replace(/\/$/, '') + '/get_bets';
  
  const payload = {
    'fromDate': fromDateStr,
    'toDate': toDateStr
  };
  
  const options = {
    'method': 'post',
    'headers': {
      'x-api-key': token,
      'Content-Type': 'application/json'
    },
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  Logger.log('Fetching bets from ' + fromDateStr + ' to ' + toDateStr);
  
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  
  if (responseCode !== 200) {
    throw new Error('Failed to fetch bets. Status: ' + responseCode + ', Response: ' + response.getContentText());
  }
  
  const data = JSON.parse(response.getContentText());
  return data.straightBets || [];
}

// ============================================
// Get existing bet IDs from sheet
// ============================================
function getExistingBetIds(sheet) {
  const existingBetIds = new Set();
  
  // Get all data from the sheet
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    // Only header row or empty sheet
    return existingBetIds;
  }
  
  // Column H contains bet-id (index 8)
  const betIdColumn = 8;
  const betIds = sheet.getRange(2, betIdColumn, lastRow - 1, 1).getValues();
  
  betIds.forEach(row => {
    if (row[0]) {
      existingBetIds.add(row[0]);
    }
  });
  
  return existingBetIds;
}

// ============================================
// Append bets to sheet
// ============================================
function appendBetsToSheet(sheet, bets, accountName) {
  const rows = [];
  
  bets.forEach(bet => {
    // Format: date, league, home-away, over points (handicap), odd, match total (f1+f2), profit (win/risk), bet-id, account-name
    
    // Parse date
    const date = new Date(bet.placedAt);
    
    // League (using leagueId for now, you may want to map this to league names)
    const league = bet.leagueId || 'N/A';
    
    // Home-Away teams
    const homeAway = bet.team1 + ' - ' + bet.team2;
    
    // Over/Under points (handicap)
    const overPoints = (bet.side || '') + ' ' + (bet.handicap || '');
    
    // Odd (price)
    const odd = bet.price || 0;
    
    // Match total (ftTeam1Score + ftTeam2Score)
    const matchTotal = (bet.ftTeam1Score || 0) + (bet.ftTeam2Score || 0);
    
    // Profit (win/risk) - use winLoss if available, otherwise calculate
    let profit;
    if (bet.betStatus === 'WON') {
      profit = bet.winLoss || bet.win || 0;
    } else if (bet.betStatus === 'LOST') {
      profit = -(bet.risk || 0);
    } else {
      profit = 0; // Pending or other status
    }
    
    // Bet ID
    const betId = bet.betId;
    
    rows.push([
      date,
      league,
      homeAway,
      overPoints,
      odd,
      matchTotal,
      profit,
      betId,
      accountName
    ]);
  });
  
  // Append all rows at once (more efficient)
  if (rows.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, 9).setValues(rows);
  }
}

// ============================================
// Create menu on open
// ============================================
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Bets Tools ⚽')
    .addItem('Fetch and Append Bets', 'fetchAndAppendBets')
    .addItem('Setup BETS sheets', 'setupSheets')
    .addToUi();
}

// ============================================
// Set API credentials in Script Properties
// ============================================
function setApiCredentials() {
  const ui = SpreadsheetApp.getUi();
  
  // Prompt for API URL
  const urlResponse = ui.prompt(
    'API URL',
    'Enter your API Base URL (e.g., https://ukkocgsw0ocgs0gkc4sgc844.coolify.sheetlife.app):',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (urlResponse.getSelectedButton() !== ui.Button.OK) {
    return;
  }
  
  const apiUrl = urlResponse.getResponseText().trim();
  
  if (!apiUrl) {
    ui.alert('API URL cannot be empty.');
    return;
  }
  
  // Prompt for API Token
  const tokenResponse = ui.prompt(
    'API Token',
    'Enter your API Token:',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (tokenResponse.getSelectedButton() !== ui.Button.OK) {
    return;
  }
  
  const apiToken = tokenResponse.getResponseText().trim();
  
  if (!apiToken) {
    ui.alert('API Token cannot be empty.');
    return;
  }
  
  // Save to Script Properties
  const scriptProperties = PropertiesService.getScriptProperties();
  scriptProperties.setProperty('API_URL', apiUrl);
  scriptProperties.setProperty('API_TOKEN', apiToken);
  
  ui.alert('API credentials saved successfully!');
}

// ============================================
// Setup function to create necessary sheets
// ============================================
function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // Create BETS sheet if it doesn't exist
  let betsSheet = ss.getSheetByName('BETS');
  if (!betsSheet) {
    betsSheet = ss.insertSheet('BETS');
    
    // Add headers
    const headers = [
      'Date',
      'League',
      'Home-Away',
      'Over Points (Handicap)',
      'Odd',
      'Match Total (F1+F2)',
      'Profit (Win/Risk)',
      'Bet ID',
      'Account Name'
    ];
    
    betsSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    betsSheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    betsSheet.setFrozenRows(1);
    
    // Auto-resize columns
    for (let i = 1; i <= headers.length; i++) {
      betsSheet.autoResizeColumn(i);
    }
  }
  
  SpreadsheetApp.getUi().alert('Setup complete! Please set your API credentials using "Set API Credentials" from the menu.');
}