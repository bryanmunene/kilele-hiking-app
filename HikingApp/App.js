import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';

const hikeData = [
  { id: '1', name: 'Mount Kenya Trek' },
  { id: '2', name: 'Ngong Hills Hike' },
  { id: '3', name: 'Karura Forest Trails' },
  { id: '4', name: 'Aberdare Ranges Adventure' },
  { id: '5', name: 'Hell\'s Gate National Park Walk' },
];

export default function App() {
  const handleHikePress = (hikeName) => {
    console.log(`Pressed: ${hikeName}`);
    // In the future, we'll navigate to the details screen for this hike
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select Your Hike</Text>
      <ScrollView style={styles.hikeListContainer}>
        {hikeData.map((hike) => (
          <TouchableOpacity
            key={hike.id}
            style={styles.hikeItem}
            onPress={() => handleHikePress(hike.name)}
          >
            <Text style={styles.hikeItemText}>{hike.name}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    paddingTop: 50,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  hikeListContainer: {
    flex: 1,
    paddingHorizontal: 15,
  },
  hikeItem: {
    backgroundColor: '#fff',
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  hikeItemText: {
    fontSize: 18,
  },
});